# Research Write Refine - Group 17

An evidence-grounded research and writing assistant developed for **DSS5105 Capstone - Track 3**.

## Overview

Research Write Refine supports a research workflow from literature review to a checked, refined draft:

**Literature collection -> topic clustering -> evidence review -> research proposal -> six-section first draft -> writing review -> revision -> evaluation**

The generated paper structure is Abstract, Introduction, Related Work, Methodology, Experiments and Conclusion. For a proposed study, the Experiments section describes an evaluation plan rather than completed results.

## Applications

| Application | Purpose | How to open |
|---|---|---|
| Hosted Sprint 3 demo | Browse the saved end-to-end walkthrough without an API key | [Open the live demo](https://research-write-refine-track3-grp17.streamlit.app/) |
| Sprint 3 local app | Choose a topic, review claims, inspect a first draft, follow the rewrite, compare results, and use the detector tools | `streamlit run sprint3_demo/app_sprint3.py` |
| Sprint 2 local app | Review the prepared research handover and saved writing-refinement results; an explicit live mode also supports paid refinement | `python sprint2_demo/ui/launch.py` |

The hosted app is managed from a separate repository. A commit to this repository does not by itself update the hosted copy.

## Repository folders

| Path | Contents |
|---|---|
| `src/research/` | Literature collection, sampling and pilot generation |
| `src/fact_checking/` | Evidence matching and saved pilot reporting |
| `src/detection/` | AI-likeness detector, rewrite experiments and evaluation tools |
| `src/writing/` | Writing review, revision and preservation checks |
| `research_package_automation/` | Research-package construction and reviewed-topic export tools |
| `notebooks/` | Corpus mapping, clustering and exploratory analysis |
| `data/` | Corpus, evidence and evaluation inputs |
| `docs/` | Architecture, research, deployment, evaluation and contribution documentation |
| `examples/` | Matching synthetic research-package and draft fixtures |
| `results/` | Recorded experiment and evaluation outputs |
| `sprint3_demo/` | Sprint 3 Streamlit app and saved five-topic walkthrough bundles |
| `sprint2_demo/` | Sprint 2 Streamlit app, pinned backend, prepared inputs and saved runs |
| `tests/` | Root writing and repository checks |

Three compatibility launchers remain at their earlier `src/` paths. The maintained research and fact-checking implementations are in the folders listed above; see [contributions and integration history](docs/contributions.md) for the moved-file map.

## Requirements

- Python **3.12**
- A virtual environment is recommended
- Git, to clone the repository

Install only the dependency set needed for the task:

| File | Use |
|---|---|
| `sprint3_demo/requirements.txt` | Sprint 3 app |
| `sprint2_demo/requirements.txt` | Sprint 2 app and saved-results launcher |
| `requirements.txt` | Research notebooks, detector training and the pilot fact checker |
| `research_package_automation/requirements.txt` | Research-package automation tools |
| `sprint2_demo/ui/requirements.txt` | Minimal Sprint 2 interface environment |

Some root research dependencies are large. Do not run collection, sampling, training or generation scripts merely to browse a demo; they may download data, overwrite experiment outputs or make paid API calls.

## Clone and set up

```sh
git clone https://github.com/joeywze/research-write-refine-track3.git
cd research-write-refine-track3
python3.12 -m venv .venv
```

Activate the environment:

```sh
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Upgrade `pip`, then install the requirements for the app you want to run:

```sh
python -m pip install --upgrade pip

# Sprint 3
python -m pip install -r sprint3_demo/requirements.txt

# Or Sprint 2
python -m pip install -r sprint2_demo/requirements.txt
```

## Run the Sprint 3 app

From the repository root:

```sh
streamlit run sprint3_demo/app_sprint3.py
```

The four-step walkthrough uses saved bundles, so it does not require an API key. Detector scoring for pasted text also runs locally. Rewriting new pasted text is optional and uses the OpenAI API; see [Optional paid API features](#optional-paid-api-features).

## Run the Sprint 2 app

The default launcher shows saved research and writing results and explicitly disables paid calls:

```sh
python sprint2_demo/ui/launch.py
```

Open the loopback address printed by the launcher. If the default port is occupied, choose another one:

```sh
python sprint2_demo/ui/launch.py --port 8502
```

To enable the separate, explicit paid-refinement mode:

```sh
python sprint2_demo/ui/launch.py --live --port 8502
```

The live launcher reads an existing `OPENAI_API_KEY` from the process environment or asks for one at a hidden prompt. It retains the existing spending ledger and process locks. Do not delete or reset them to bypass a failed or interrupted run. See the [Sprint 2 demo guide](sprint2_demo/README.md) for the workflow and limitations.

## Optional paid API features

The repository can be explored, and both saved demo workflows can be viewed, without making paid calls.

- **Sprint 3:** new-text rewriting becomes available locally when `OPENAI_API_KEY` is set in the environment or in an ignored `.env` file at the repository root. The saved walkthrough and local detector scoring remain available without it.
- **Sprint 2:** the default launcher removes any ambient API key and disables paid calls. Paid refinement is enabled only with the `--live` flag.
- **Research and evaluation scripts:** some generation, fact-checking and detector experiments may also call external APIs. Review the relevant module documentation before running them.

Never commit API keys, `.env` files, private drafts, identifiable reviewer responses or Streamlit secrets. The repository ignores `.env` and `.private/` for future local files, but adding a path to `.gitignore` does not remove anything already present in Git history. Use fresh credentials if a secret has ever been committed.

## Tests and validation

The following checks are offline and use fixtures or mocked model providers; they do not require paid API calls:

```sh
# Root writing and repository tests
python -m unittest discover -s tests -v

# Validate the synthetic research-package and draft contract
python -m src.writing validate \
  --package examples/research_package.json \
  --v0 examples/v0.json

# Sprint 2 integration and guard tests
python -m unittest discover -s sprint2_demo -p 'test_*.py' -v

# Sprint 2 interface tests
cd sprint2_demo/ui
python -m unittest test_app test_research test_detection -v
```

See [evaluation and failure analysis](docs/evaluation.md) for the full test matrix and the distinction between offline tests, saved model runs, deliberate safety tests and independent human evaluation.

Validation checks confirm software contracts such as package structure, required sections, claim coverage, evidence references and citation links. They do **not** establish scientific correctness, approve a research claim, prove authorship, or independently validate the quality of a generated paper.

## Troubleshooting

| Problem | What to check |
|---|---|
| `python3.12` is not found | Install Python 3.12, then recreate the virtual environment with that interpreter. |
| `streamlit` or another module is missing | Activate `.venv` and install the requirements file for the selected app. |
| The app does not open automatically | Copy the local URL printed in the terminal into a browser. |
| Port 8501 is already in use | Keep the existing server or start Sprint 2 on another port with `--port 8502`. For Sprint 3, add `--server.port 8502` to the `streamlit run` command. |
| Sprint 3 can score but cannot rewrite new text | Set `OPENAI_API_KEY` locally. The online preview intentionally disables rewriting of new text. |
| Sprint 2 paid refinement is unavailable | Start the launcher with `--live` and provide a valid key. The default launcher intentionally removes API credentials. |
| A restricted Windows environment reports a Streamlit socket error during tests | Run the interface tests outside that restricted environment; Streamlit's local asyncio socket pair may be blocked. |
| A hosted change is not visible | Confirm the hosted app's repository, branch, commit and Python version with the deployment owner. This repository does not control the separate hosted copy. |

## Scope and interpretation

- The prepared case study is a research proposal, not a completed multilingual experiment or a confirmed novelty claim.
- Saved pilot support labels and detector outputs are recorded results; they are not regenerated on page load.
- Writing-review counts and detector scores measure different things. Neither establishes factual accuracy or proves authorship.
- Preservation checks reduce risk but cannot guarantee unchanged meaning.
- The root [`examples/`](examples/README.md) files are synthetic software-test fixtures. The prepared research package and matching first draft used by the demo are pinned under `sprint2_demo/inputs/converted/`.

## Documentation

- [Architecture and source-of-truth boundaries](docs/architecture.md)
- [Research proposal, citations and unresolved decisions](docs/research/README.md)
- [Writing workflow](docs/writing_workflow.md)
- [Evaluation and failure analysis](docs/evaluation.md)
- [Deployment and hosted-copy notes](docs/deployment.md)
- [Contributions and integration history](docs/contributions.md)
