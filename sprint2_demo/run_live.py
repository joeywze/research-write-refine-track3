"""Run the provisional handover with a persistent, conservative dollar guard."""
from datetime import datetime, timezone
from decimal import Decimal
import argparse
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import sys

from handover import ROOT, Draft, ResearchPackage, LockedTablesGate, read, render, write_json
from src.writing.critic import QualitativeCritic
from src.writing.pipeline import RunConfig, run_study
from src.writing.preservation import SemanticGate
from src.writing.providers import BudgetExceeded, OpenAIJSON, TokenBudget
from src.writing.prompts import PROMPT_VERSION
from src.writing.storage import RunStore

WRITER = "gpt-5.4-mini-2026-03-17"
CHECKER = "gpt-5.4-2026-03-05"
RATES = {WRITER: (Decimal("0.75"), Decimal("4.50")), CHECKER: (Decimal("2.50"), Decimal("15.00"))}
PRICING = {
    "checked_date": "2026-10-25", "currency": "USD", "basis": "Standard uncached text token rates per million; cached discounts ignored",
    "sources": ["https://developers.openai.com/api/docs/models/gpt-5.4-mini", "https://developers.openai.com/api/docs/models/gpt-5.4"],
    "scope": "Only calls made through this runner. Provider invoices, taxes and other applications are outside this ledger.",
}


class DollarGuard:
    def __init__(self, path, ceiling=Decimal("10")):
        self.path = Path(path)
        self.ceiling = Decimal(ceiling)
        if self.ceiling <= 0 or self.ceiling > 10:
            raise ValueError("This pilot is authorised for at most USD 10")
        self.state = json.loads(read(self.path)) if self.path.exists() else {
            "ceiling_usd": str(self.ceiling), "pricing": PRICING, "records": []}
        if Decimal(self.state["ceiling_usd"]) != self.ceiling:
            raise ValueError("Existing spending ledger has a different ceiling; inspect it before changing budgets")

    @property
    def charged(self):
        return sum((Decimal(r["charged_estimate_usd"]) for r in self.state["records"]), Decimal(0))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".pending.json")
        temp.write_text(json.dumps(self.state, indent=2) + "\n", encoding="utf-8", newline="\n")
        temp.replace(self.path)

    def reserve(self, task, model, instructions, payload, schema, cap):
        if model not in RATES:
            raise ValueError("No verified pricing for model " + model)
        if type(cap) is not int or cap < 1:
            raise ValueError("Output limit must be positive")
        body = {"model": model, "instructions": instructions,
                "input": json.dumps(payload, ensure_ascii=False, sort_keys=True),
                "text": {"format": {"type": "json_schema", "name": "stage_b_response", "schema": schema, "strict": True}},
                "max_output_tokens": cap, "store": False}
        # One input token per UTF-8 request byte plus an overhead margin is deliberately conservative.
        # Reserve the full output allowance, including any reasoning tokens counted in it.
        input_bound = len(json.dumps(body, ensure_ascii=False).encode("utf-8")) + 8192
        incoming, outgoing = RATES[model]
        hold = (Decimal(input_bound) * incoming + Decimal(cap) * outgoing) / Decimal(1_000_000)
        if self.charged + hold > self.ceiling:
            raise BudgetExceeded("The next call's conservative cost reservation would exceed the remaining USD 10 pilot budget")
        record = {"task": task, "model": model, "input_token_bound": input_bound, "output_token_cap": cap,
                  "reservation_usd": str(hold), "charged_estimate_usd": str(hold), "status": "RESERVED_UNKNOWN_USAGE"}
        self.state["records"].append(record)
        self.save()  # Keep the reservation if the request or process fails.
        return len(self.state["records"]) - 1

    def settle(self, index, usage, not_sent=False):
        record = self.state["records"][index]
        if not_sent:
            record.update(charged_estimate_usd="0", status="NOT_SENT")
        elif usage is not None:
            incoming, outgoing = RATES[record["model"]]
            estimate = (Decimal(usage["input_tokens"]) * incoming + Decimal(usage["output_tokens"]) * outgoing) / Decimal(1_000_000)
            record.update(charged_estimate_usd=str(estimate), usage=usage, status="REPORTED_TOKENS_STANDARD_RATE_ESTIMATE")
        self.save()
        if self.charged > self.ceiling:
            raise BudgetExceeded("Reported usage exceeded the conservative reservation; no further calls are permitted")


class GuardedProvider(OpenAIJSON):
    def __init__(self, *args, dollar_guard, **kwargs):
        super().__init__(*args, **kwargs)
        self.dollar_guard = dollar_guard

    def generate(self, task, instructions, payload, schema, max_output_tokens):
        index = self.dollar_guard.reserve(task, self.model, instructions, payload, schema, max_output_tokens)
        print(f"Starting {task} ({self.stage}). Estimated budget used or reserved: USD {self.dollar_guard.charged:.4f} / 10.", flush=True)
        path = self.store.directory / "events.jsonl"
        before = len(read(path).splitlines()) if path.exists() else 0
        not_sent = False
        try:
            return super().generate(task, instructions, payload, schema, max_output_tokens)
        except BudgetExceeded:
            not_sent = True  # The base provider rejects a token reservation before calling the SDK.
            raise
        finally:
            events = [json.loads(line) for line in read(path).splitlines()[before:]] if path.exists() else []
            calls = [e for e in events if e.get("kind") == "model_call" and e.get("task") == task and e.get("stage") == self.stage]
            usage = calls[-1].get("usage") if calls else None
            self.dollar_guard.settle(index, usage, not_sent=not_sent)
            print(f"Finished {task} ({self.stage}). Estimated budget used or reserved: USD {self.dollar_guard.charged:.4f} / 10.", flush=True)


class TableAwareWriter:
    def __init__(self, provider, locked):
        self.provider = provider
        self.model, self.test_only = provider.model, provider.test_only
        self.locked = locked

    def generate(self, task, instructions, payload, schema, cap):
        instruction = instructions + "\n\nIntegration constraint: paragraph blocks " + ", ".join(self.locked)
        instruction += " are supplied Markdown tables. Keep them exactly unchanged; return edits only for other allowed blocks."
        return self.provider.generate(task, instruction, payload, schema, cap)


class SafeResponses:
    def __init__(self, responses):
        self.responses = responses

    def create(self, **kwargs):
        try:
            return self.responses.create(**kwargs)
        except Exception as error:
            # Authentication errors can contain a masked key. Keep them out of draft logs.
            status = getattr(error, "status_code", None)
            raise RuntimeError(f"OpenAI request failed ({type(error).__name__}, HTTP {status}); check credentials, model access and request configuration") from None


def prepare(input_dir=None):
    if input_dir is not None:
        from project_io import read_input
        return read_input(input_dir)
    converted = ROOT / "inputs/converted"
    package = ResearchPackage.from_dict(json.loads(read(converted / "research_package.json")))
    v0 = Draft.from_dict(json.loads(read(converted / "v0.json")), package)
    manifest = json.loads(read(converted / "handover_manifest.json"))
    return package, v0, manifest


def implementation_snapshot():
    files = sorted((ROOT / "backend/src/writing").glob("*.py"))
    files += [ROOT / name for name in ("handover.py", "run_live.py", "citation_calibration.py", "project_io.py")]
    return {"stage_b_source_revision": "f108a13eb6625fccc80bc5d57d435797519a1255",
            "research_source_revision": "01915001d9490914eb2f1a316c1ea06053adfaef",
            "local_patch": "feedback-stability-v1+project-input-v1", "prompt_version": PROMPT_VERSION,
            "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Make paid model calls; otherwise check setup only")
    parser.add_argument("--allow-provisional", action="store_true", help="Test the provisional package without implying Team A approval")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--input-dir", type=Path, help="A checked package/draft pair saved by the local interface")
    parser.add_argument("--calibrate-first", action="store_true", help="Require the fixed development cases to pass before the writing run")
    args = parser.parse_args()
    package, v0, manifest = prepare(args.input_dir)
    if args.calibrate_first and args.input_dir is not None:
        parser.error("The fixed development calibration applies only to the pinned example.")
    setup = {"writer": WRITER, "checker_and_critic": CHECKER, "maximum_total_estimated_api_spend_usd": 10,
             "credential_available": bool(os.environ.get("OPENAI_API_KEY", "").strip()),
             "openai_sdk_installed": importlib.util.find_spec("openai") is not None,
             "paragraph_blocks": len(v0.paragraphs), "locked_tables": sum(b["locked"] for b in manifest["blocks"]),
             "input_origin": manifest.get("input_origin", "pinned_example"),
             "team_a_approval": "PENDING" if args.input_dir is None else "NOT_VERIFIED", "semantic_grounding": "NOT_CHECKED", "model_calls": 0}
    if not args.execute:
        print(json.dumps(setup, indent=2))
        return 0
    if not args.allow_provisional:
        parser.error("This is a provisional handover. Use --allow-provisional for a development test.")
    if not setup["credential_available"]:
        parser.error("OPENAI_API_KEY is not configured in this process. No model calls were made.")
    if not setup["openai_sdk_installed"]:
        parser.error("Install the OpenAI SDK in the Python environment running this script.")

    lock = ROOT / "pilot_spend.lock"
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        parser.error("Another pilot may be running. Inspect pilot_spend.lock and the spending ledger before restarting.")
    os.close(handle)
    lock.write_text(str(os.getpid()), encoding="ascii")
    store = None
    try:
        from openai import OpenAI
        output = args.output or ROOT / "runs" / datetime.now(timezone.utc).strftime("live-%Y%m%dT%H%M%S%fZ")
        store = RunStore(output)
        store.write("input_manifest.json", manifest)
        write_json(ROOT / "verification/active_worker_runtime.json", {
            "pid": os.getpid(), "run": str(output), "started_utc": datetime.now(timezone.utc).isoformat(),
            "key_saved_to_file": False})
        guard = DollarGuard(ROOT / "pilot_spend.json")
        client = OpenAI(max_retries=0, timeout=180)
        client.responses = SafeResponses(client.responses)
        locked = [b["paragraph_id"] for b in manifest["blocks"] if b["locked"]]

        def pair(stage):
            token_budget = TokenBudget(1_000_000)
            provider = GuardedProvider(WRITER, token_budget, store, client=client, stage=stage, dollar_guard=guard)
            checker = GuardedProvider(CHECKER, token_budget, store, client=client, stage=stage, dollar_guard=guard)
            return TableAwareWriter(provider, locked), LockedTablesGate(SemanticGate(checker, max_output_tokens=16000), manifest)

        store.write("integration_configuration.json", {"setup": setup, "provisional": True,
            "writer_output_cap": 16000, "preservation_output_cap": 16000, "critic_output_cap": 32000,
            "per_stage_token_limit": 1_000_000, "max_attempts": 3, "locked_table_ids": locked,
            "explanation": "Full-document output caps; the loop and acceptance rules are unchanged.",
            "pricing": PRICING, "implementation": implementation_snapshot(),
            "calibration_required": args.calibrate_first})
        try:
            if args.calibrate_first:
                from citation_calibration import run_calibration

                def calibration_provider(stage):
                    return GuardedProvider(CHECKER, TokenBudget(1_000_000), store, client=client,
                                           stage=stage, dollar_guard=guard)

                calibration = run_calibration(package, v0, calibration_provider, store)
                if calibration["status"] != "PASS":
                    store.event("writing_run_blocked", reason="Unexpected development calibration verdict; no writing run started")
                    print(json.dumps({"status": "CALIBRATION_FAILED", "run": str(store.directory.resolve()),
                                      "estimated_total_spend_usd": str(guard.charged)}, indent=2))
                    return 2
            baseline_writer, baseline_gate = pair("v0")
            arms = {a: pair(a) for a in ("generic", "guided")}
            critic_provider = GuardedProvider(CHECKER, TokenBudget(1_000_000), store, client=client,
                                              stage="critique", dollar_guard=guard)
            critic = QualitativeCritic(critic_provider, max_output_tokens=32000)
            summary = run_study(package, v0, baseline_writer, baseline_gate, arms, store,
                                RunConfig(max_output_tokens=16000), critic=critic)
        finally:
            # Preserve readable exports even if V0 fails grounding before revision starts.
            for name in ("v0_input", "v0_accepted", "generic_final", "guided_final"):
                path = store.directory / (name + ".json")
                if path.exists():
                    data = Draft.from_dict(json.loads(read(path)), package)
                    (store.directory / (name + "_with_layout.md")).write_text(render(data, manifest), encoding="utf-8", newline="\n")
            store.write("spend_snapshot.json", guard.state)
        print(json.dumps({"status": summary["status"], "run": str(store.directory.resolve()),
                          "estimated_total_spend_usd": str(guard.charged), "team_a_approval": setup["team_a_approval"]}, indent=2))
        return 0
    except Exception as error:
        if store is not None:
            store.event("integration_run_failed", error_type=type(error).__name__, message=str(error))
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    finally:
        lock.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
