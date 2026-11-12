# Sprint 3 demo site

Built on the Sprint 2 site's look and components (`sprint2_demo/ui/look.py`, `detection_view.py`), which it
imports unchanged. The Sprint 2 site itself (`sprint2_demo/ui/app.py`) is untouched.

Pages (menu at the top):
- **Walkthrough**: four clickable steps. *Build the paper*: 1 Choose a topic (gap shown, claims reviewed or
  skipped), 2 First draft. *Polish the writing*: 3 Rewrite (checks, attempts, holds, hard case), 4 Compare
  and download. Back / Next stay at the bottom right of the window.
- **Score and rewrite your text**: paste a paragraph or upload a paper; rewriting runs only locally.
- **Detector and tests**: the Sprint 2 detector pages.

Everything in the walkthrough is pre-built from saved runs, so the hosted site needs no API key.

1. After the final pipeline runs (`sprint2_demo/runs/half2-final-<topic>`), build the topic files:
   `python sprint3_demo/build_demo_bundles.py`  (writes `sprint3_demo/bundles/*.json`; commit them)
2. Run locally: `streamlit run sprint3_demo/app_sprint3.py`
   Rewriting pasted text works locally when OPENAI_API_KEY is in the repo's .env file (or the environment).
3. Deploy on Streamlit Community Cloud with main file `sprint3_demo/app_sprint3.py`.
