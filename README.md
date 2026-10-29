# Research Write Refine — Group 17

An evidence-grounded research and writing assistant developed for **DSS5105 Capstone — Track 3**.

[Open the live demo](https://research-write-refine-track3-grp17.streamlit.app/)

## Project workflow

**Literature collection → Topic clustering → Evidence review → Research proposal → Draft V0 → Writing review → Revision → Evaluation**

The paper follows Abstract, Introduction, Related Work, Methodology, Experiments and Conclusion. For a proposed study, Experiments describes an evaluation plan rather than completed results.

## Explore the project

| Workstream | Start here |
|---|---|
| Research development | [Research guide](src/research/README.md), [analysis notebooks](notebooks/), [proposal and evidence review](docs/research/README.md) |
| Evidence checking | [Fact-checking guide](src/fact_checking/README.md), [claim ledger](docs/research/claim_evidence_ledger.json), [saved pilot assessments](data/facts/pilot/draft_v0_pilot_verification.csv) |
| Writing refinement | [Writing workflow](docs/writing_workflow.md), [input contract](docs/stage_b.md), [writing backend](src/writing/) |
| Detection and evaluation | [Detector guide](src/detection/README.md), [evaluation guide](docs/evaluation.md), [recorded results](results/README.md) |
| Streamlit application | [Demo guide](sprint2_demo/README.md), [deployment guide](docs/deployment.md) |

## Current progress and scope

| Capability | Status |
|---|---|
| Literature clustering and research development | Initial Cluster 7 case study prepared |
| Research package and six-section V0 | Prepared; evidence verification, design decisions and team approval remain open |
| Writing review, revision and rollback | Prototype implemented; recorded model runs available |
| Streamlit interface and public deployment | Available; this repository does not control the separate hosted copy |
| Detector experiments, held-out tests and human evaluation | Tools and development outputs available; independent human assessment remains necessary |
| Reusable paper selection → AI analysis → human-approved package | Planned for Sprint 3; not implemented as a new-topic workflow |

## Repository structure

```text
src/
  research/          Literature collection and pilot generation
  fact_checking/     Evidence matching and saved pilot reporting
  detection/         Detector, rewrite experiments and evaluation tools
  writing/           Writing review, revision and preservation checks
notebooks/           Corpus mapping, clustering and exploratory analysis
data/                Corpus, evidence and evaluation inputs
examples/            Matching synthetic package and V0; links to the real example
results/             Documented experiment and evaluation outputs
docs/
  research/          Evidence review, proposal and research-paper V0
  architecture.md    Components, handover and pinned demo boundary
  evaluation.md      Test suites and evaluation limitations
  deployment.md      Hosted demo and local setup
  contributions.md   Team workstreams and integration provenance
sprint2_demo/        Stable Streamlit entrypoint, pinned backend and saved runs
tests/               Root writing and repository checks
```

Three small launchers remain at their old `src/` paths for compatibility; maintained research and fact-checking code is in the folders above. The moved-file map and branch revisions are recorded in [contributions](docs/contributions.md).

## Run locally

Use Python 3.12 and a virtual environment. From the repository root:

```sh
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r sprint2_demo/requirements.txt
python sprint2_demo/ui/launch.py
```

Open the address printed by the launcher. The default mode removes any ambient API key and disables paid model calls. The hosted preview and default local mode display saved research and writing results; local detector scoring does not call an API. Fresh model refinement requires the explicit local live setup described in the [demo guide](sprint2_demo/README.md).

Install root `requirements.txt` additionally for research notebooks, detector training and the pilot fact checker. Some research dependencies are large. Do not run collection, sampling, training or generation scripts merely to browse the demo: they can download data, overwrite experiment outputs or make paid calls.

## Tests and examples

```sh
python -m unittest discover -s tests -v
python -m src.writing validate --package examples/research_package.json --v0 examples/v0.json
```

See [evaluation](docs/evaluation.md) for the pinned-backend, handover and Streamlit test commands. Offline tests use fixtures or mocked model providers, not paid API calls.

The root [examples](examples/README.md) are synthetic software-test fixtures. The real prepared research package and matching V0 are pinned under `sprint2_demo/inputs/converted/`. Source snapshots and recorded results remain unchanged so the demonstration is reproducible.

## Interpretation and limitations

- The case study is a research proposal, not a completed multilingual experiment or a confirmed novelty claim.
- Seven saved pilot claims were assessed: three supported and four needing further review. These labels are not newly generated on page load or by evidence retrieval.
- Upload validation checks structure and citation links, not scientific correctness.
- Writing-review counts and detector scores are different measures. Neither establishes factual accuracy or proves authorship.
- Preservation checks reduce risk but do not guarantee unchanged meaning.
- Live runs, dry runs, deliberate safety tests and independent evaluation must be interpreted separately. See the [results index](results/README.md).
- A detector-generated `final_paper_v3.md` is an experiment output, not team approval or final submission.
- Historical evaluation keys already committed to a public repository are not private. Never show keys to blinded raters; use fresh evaluation items if raters have seen the keys.
- Keep credentials and identifiable reviewer responses out of Git. `.private/` is ignored for future local-only materials; ignoring a path does not erase files already in Git history.

## Documentation and team

- [Architecture and source-of-truth boundaries](docs/architecture.md)
- [Research proposal, citations and unresolved decisions](docs/research/README.md)
- [Evaluation and failure analysis](docs/evaluation.md)
- [Deployment and the separate hosted repository](docs/deployment.md)
- [Contributions and integration history](docs/contributions.md)

| Workstream | Contributors |
|---|---|
| Research development, evidence checking and handover | Tabitha / Joey / Silvia |
| Writing refinement, interface and evaluation tools | Guan Hong / Wan Yun / Lili |
| Integration, validation and final deliverables | Entire team |

