# Sprint 2 interface

The four-step journey is Research → Draft → Refine → Results. It loads the full provisional research handover, the inspected real model run and earlier unsuccessful comparisons. It also connects to the existing live backend and runs the actual number-change preservation test.

## Open locally

The prepared environment is `ui/.venv`. Open `Open demo.cmd`, then visit http://127.0.0.1:8501. This mode needs no key and disables paid calls. Keep the launcher open while using the app. If another copy is already running on 8501, use that copy or stop it before starting another.

For a clean setup with Python 3.12:

```powershell
cd ui
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\Open demo.cmd
```

The app's default is a clearly labelled replay of recorded real outputs. It does not pretend to regenerate the literature review or initial draft. The source warnings and pending Team A approval remain visible. Downloads contain the complete saved paper, including headings, references and tables.

## New live refinement

To enable paid refinement locally, open `Open live demo.cmd`, enter the key at its hidden prompt and keep the window open. This separate local server uses http://127.0.0.1:8502. The key lives only in server/child environments; it is not saved in a file, browser input, job record or download. The Refine screen then enables “Refine draft”. It launches `run_live.py` on the current complete package and V0, without repeating the five preliminary calibration cases. It performs the same V0 check, initial critique, generic comparison and bounded guided loop already tested at the backend.

A separate launch lock blocks duplicate clicks across sessions; the existing runner also enforces its persistent US$10 ledger and process lock. There are no automatic retries. Refreshing or moving between screens does not launch another run. The UI polls stage markers and offers the completed saved result. Keep the server alive during a run; an interrupted call may retain an unknown-usage reservation. Do not delete locks or reset the ledger to bypass a failed or interrupted run.

The browser-to-model path was verified on 26 October in `live-20261026T000828046240Z`: one browser click started the real runner, one guided revision was accepted, and the completion control opened that run's result. The downloaded Markdown hash matched the saved accepted file. The number-change test on this new output was rejected and retained the accepted draft. This run used six API calls, about 136.9 seconds summed model time and an estimated US$0.4057 at the saved standard rates. Its LLM review-point count fell from 2 to 0; the generic arm retained V0. This remains development evidence rather than independent quality validation.

The live check exposed a completed-run navigation bug. It was fixed by requesting a full app rerun from the fragment, and a regression test now checks that the completion control selects and displays the intended result. The approved Research layout has 20 passing interface and research-record checks; the upload-validation checks remain separate. No repeat model run was needed for that UI fix.

## Safety demonstration

“Test a change to a study detail” injects 20 → 21 into the currently accepted guided draft and invokes the real preservation/rollback code. It forces that paragraph into scope for the test. It does not call a model or claim that the writer produced the injected error. The app displays the rejection reason and verifies that the retained draft hash matches the accepted input. Records are stored under `verification/ui-safety/`.

## Deploy the prepared candidate

`package_demo.py` creates an allow-listed deployment folder and ZIP under `deployment/`. It excludes virtual environments, credentials, browser data and temporary test files. The bundle contains a pinned Python UI, the real backend and the required saved inputs and runs. It retains the existing budget ledger for provenance.

For a container host, from the extracted bundle:

```text
docker build -t track3-sprint2 .
docker run --rm -p 8501:8501 track3-sprint2
```

The current Streamlit Community Cloud preview uses `tangh86/research-write-refine-track3`, branch `UI-demo`, Python 3.12 and main file `sprint2_demo/ui/app.py`. The same source is available for team review on `joeywze/research-write-refine-track3`, branch `sprint2-ui-demo`, in draft PR #5. See `DEPLOY.md` for deployment details.

The bundle supplies `.streamlit/config.toml` at both the root and app directory. Its local launcher binds explicitly to loopback; hosted settings use the host's address. Streamlit's [deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) explain the repository, branch, entrypoint and Python setting. Private-repository deployment requires the appropriate GitHub access and repository administration permissions; see [Cloud access requirements](https://docs.streamlit.io/deploy/streamlit-community-cloud/status).

Hosted mode binds beyond loopback and blocks paid live launches even if an API key is accidentally configured. It still provides recorded outputs, downloads and the executable local-number safety test. Public live inference would need a separate authenticated deployment with shared persistent accounting; it is not enabled by this bundle. Do not change repository visibility or upload the team's private draft without the team's approval.

## Recording and limitations

Use “Viewing saved results” when browsing the saved comparison, describe the content-protection check as a deliberately inserted error, and “Recorded run; waiting time shortened” if editing out real latency. The accepted model run clarified two passages; its LLM review-point count fell from 2 to 0, while fixed-rule counts stayed at 0. These are internal diagnostics, not independently established quality scores. Team A approval, source-support warnings, held-out evaluation and human ratings remain unresolved.

Automated interface and research-record checks use `python -m unittest test_app test_research -v` from `ui`. They cover the four screens, actual safety rollback, accepted-file download content, earlier failed outputs and live-launch guards. On restricted Windows sandboxes, Streamlit's local asyncio socket pair may require running the tests outside the sandbox.

## Choose a research project

Research opens the prepared proposal. It shows the literature-to-handover workflow, proposed gap and seven findings from the saved pilot review. Each finding brings its passage, paper link and existing support label together. Preparation details contain methods, the 18 topic papers and source identifiers. The display is pinned to the original Stage A records; it neither starts literature processing nor assigns new support labels. The 3 supported and 4 unresolved pilot claims remain distinct from a complete fact check.

To open another package, expand **Use another prepared project**. Upload `research_package.json` and the matching `v0.json`, both using schema 0.1. Downloadable example files are provided in the app. Each file is limited to 1 MB; the draft can contain up to 60 content blocks and 12,000 words.

The server checks the package identity, all six sections, claim coverage, evidence references and supporting citations. Source links must use HTTPS. Tables are locked. A generated layout keeps every content block and provides citation links and references; a contract-only upload does not reproduce a separately formatted source document. These checks do not verify scientific correctness or grant research-team approval.

An upload stays in the current Streamlit session until a local refinement starts. At that point a checked copy is saved under the job's own input directory and passed explicitly to the existing budgeted runner. The saved result carries its package and layout, so it can never inherit the example's scores. Uploaded runs do not appear in the shared example selector. Reloading or losing the session may discard an unrun upload; there is no shared editing or persistent project account.

The Refine table now shows before and after counts together: the current example has rules 0 → 0 and LLM 2 → 0. Original findings are labelled separately from the accepted result. An unrun upload has blank LLM and after-refinement values, not invented zeros. The safety exercise is available for the example; its deliberately chosen pilot-size edit is not applied to arbitrary uploads.

No additional paid run was made for the upload feature. Its validation, input forwarding and interface behaviour were checked offline; the earlier example run remains the live-model evidence. Arbitrary topic entry is outside the Sprint 2 journey. Stage A prepares the package before the demo; this screen inspects its output.
