# Deployment and local setup

[Open the current demo](https://research-write-refine-track3-grp17.streamlit.app/)

The team supplied this URL as the current demo. Hosting is managed from a team member's separate repository. The owner should confirm its current repository, branch, commit and Python version; the URL alone does not establish those settings. A change in this integration branch does not update the hosted app.

## Stable entrypoint

Keep `sprint2_demo/ui/app.py`. Source snapshots, saved runs, converted inputs, detector model and result paths are unchanged by this cleanup. The earlier [deployment record](../sprint2_demo/DEPLOY.md) documents the original preview and must not be read as confirmation of the new host configuration.

The detector-enhanced interface reads repository-level `src/detection/`, `results/detection/` and `data/human_eval/`. A deployment that copies only the old `sprint2_demo/` bundle will omit these additions. Deploy the complete reviewed checkout for the five-step app; packaging a new self-contained Docker bundle is separate work. Do not assume the historical Docker bundle includes the detector step.

## Local saved-results mode

From the repository root, in a Python 3.12 virtual environment:

```sh
python -m pip install -r sprint2_demo/requirements.txt
python sprint2_demo/ui/launch.py
```

The launcher binds to loopback, prints the URL, removes ambient `OPENAI_API_KEY` and disables paid calls. Use `--port 8502` if another application occupies the default port. Do not stop another team's server just to reuse its port.

## Local live mode

```sh
python sprint2_demo/ui/launch.py --live --port 8502
```

This is an explicit paid-inference mode. The launcher accepts a temporary key at a hidden prompt or from the existing process environment; it does not save the key in files. No live call was required to organise the repository.

The live runner retains its existing persistent spending ledger and process locks. Do not reset or delete them to bypass a failed run, and do not treat a copied historical ledger as a shared multi-host accounting system.

## Hosted preview

Keep API keys out of public source and preview configuration. The current guards disable paid launches beyond loopback. Public live inference would require separately reviewed authentication, abuse prevention and persistent shared accounting; it is not enabled by this reorganisation.

Before updating the hosted copy, agree the reviewed source commit with the deployment owner. Check Research, Draft, Refine, Results and Detect; verify package/draft downloads, the saved source warnings, and the deliberate rollback exercise. Do not claim a successful deployment solely because local tests pass.
