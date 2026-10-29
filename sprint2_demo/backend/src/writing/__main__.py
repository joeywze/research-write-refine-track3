"""Draft, revise and assess research writing with python -m src.writing."""

import argparse
import json
from pathlib import Path

from .contracts import Draft, ResearchPackage
from .critic import QualitativeCritic
from .diagnostics import diagnose
from .evaluation import export_human, held_out_audit, read_json
from .pipeline import RunConfig, run_study
from .preservation import SemanticGate
from .providers import OpenAIJSON, TokenBudget
from .storage import RunStore


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Check package and draft formats without model calls")
    validate.add_argument("--package", type=Path, required=True)
    validate.add_argument("--v0", type=Path)
    run = commands.add_parser("run", help="Check V0 and run generic and guided revision using live models")
    run.add_argument("--package", type=Path, required=True)
    run.add_argument("--v0", type=Path, help="Initial draft; omit to generate one before checking its content")
    run.add_argument("--writer-model", required=True)
    run.add_argument("--checker-model", required=True)
    run.add_argument("--method", choices=("rules-critic", "rules-only"), default="rules-critic",
                     help="Use rule-based checks and LLM writing review by default; rules-only is the comparison method")
    run.add_argument("--critic-model", help="LLM writing review model; defaults to the chosen checker model in a separate call")
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--max-attempts", type=int, default=3)
    run.add_argument("--min-improvement", type=float, default=1.0)
    run.add_argument("--max-output-tokens", type=int, default=6000)
    run.add_argument("--token-limit", type=int, default=200_000, help="Separate token allowance for V0, each revision version and the critic when used")
    measure = commands.add_parser("measure", help="Measure writing features offline without adding edit rules")
    measure.add_argument("--package", type=Path, required=True)
    measure.add_argument("--v0", type=Path, required=True)
    measure.add_argument("--output", type=Path, required=True)
    demo = commands.add_parser("demo", help="Try the workflow offline with scripted responses and synthetic data")
    demo.add_argument("--output", type=Path, required=True)
    export = commands.add_parser("export-human", help="Prepare anonymised texts and evidence for independent review")
    export.add_argument("--runs", type=Path, nargs="+", required=True)
    export.add_argument("--output", type=Path, required=True)
    export.add_argument("--seed", type=int, default=42)
    audit = commands.add_parser("audit", help="Check preservation with a separate evaluator model")
    audit.add_argument("--run", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    audit.add_argument("--evaluator-model", required=True)
    audit.add_argument("--token-limit", type=int, default=200_000)
    args = parser.parse_args(argv)
    store = None
    try:
        if args.command == "demo":
            from .demo import run_demo
            result = run_demo(args.output)
        elif args.command == "export-human":
            result = export_human(args.runs, args.output, args.seed)
        elif args.command == "audit":
            result = {"audits": len(held_out_audit(args.run, args.output, args.evaluator_model, args.token_limit))}
        else:
            package = ResearchPackage.from_dict(read_json(args.package))
            v0 = Draft.from_dict(read_json(args.v0), package) if args.v0 else None
            if args.command == "validate":
                result = {"schema_valid": True, "all_six_sections": v0 is not None,
                          "semantic_grounding": "NOT_CHECKED"}
            elif args.command == "measure":
                store = RunStore(args.output)
                result = diagnose(v0)
                store.write("diagnostics.json", result)
            else:
                config = RunConfig(args.max_attempts, args.min_improvement, args.max_output_tokens)
                if args.writer_model.casefold().strip() == args.checker_model.casefold().strip():
                    raise ValueError("Writer and preservation checker must use different model IDs")
                if args.method == "rules-only" and args.critic_model is not None:
                    raise ValueError("Use --critic-model with rules-critic, or omit it for rules-only")
                critic_model = None
                if args.method == "rules-critic":
                    critic_model = args.critic_model if args.critic_model is not None else args.checker_model
                if critic_model is not None and (not critic_model.strip() or
                        critic_model.casefold().strip() == args.writer_model.casefold().strip()):
                    raise ValueError("The style critic needs a non-empty model ID distinct from the writer")
                TokenBudget(args.token_limit)  # Check the limit before creating output files.
                store = RunStore(args.output)

                def pair(stage):
                    budget = TokenBudget(args.token_limit)
                    return (OpenAIJSON(args.writer_model, budget, store, stage=stage),
                            SemanticGate(OpenAIJSON(args.checker_model, budget, store, stage=stage)))

                writer, gate = pair("v0")
                arms = {arm: pair(arm) for arm in ("generic", "guided")}
                critic = (QualitativeCritic(OpenAIJSON(critic_model, TokenBudget(args.token_limit),
                                                      store, stage="critique")) if critic_model else None)
                store.write("budget_configuration.json", {"token_limit_each_stage_or_arm": args.token_limit,
                                                          "max_stage_or_arm_count": 4 if critic else 3,
                                                          "basis": "conservative input reservation, reported usage when available"})
                result = run_study(package, v0, writer, gate, arms, store, config, critic=critic)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        if store is not None:
            store.event("run_failed", error_type=type(error).__name__, message=str(error))
        parser.exit(1, f"{type(error).__name__}: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
