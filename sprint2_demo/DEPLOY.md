# Deploy the team review preview

The app is ready on `sprint2-ui-demo`. A repository admin needs to deploy it: Streamlit Cloud requires admin access, while the current contributor account has write access. No merge into `main` or `stage-b-development` is needed.

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with a GitHub account that has admin access to `joeywze/research-write-refine-track3`. Allow access to this private repository if required.
2. Select **Create app → Deploy from repo**.
3. Use these settings:

| Setting | Value |
| --- | --- |
| Repository | `joeywze/research-write-refine-track3` |
| Branch | `sprint2-ui-demo` |
| Main file | `sprint2_demo/ui/app.py` |
| Python version | `3.12`, under Advanced settings |
| Secrets | Leave empty |

4. Deploy and wait for the app to open. Keep it private for team review, then give the intended team members viewing access. App access and permission to edit the GitHub source are separate.
5. Check Research, Draft, Refine and Results. In the example, rule counts are 0 → 0 and LLM review points are 2 → 0. Try the study-detail change test and confirm it is rejected. Download the refined draft.

The preview uses saved real-model results. It can check uploaded research-package/draft files and run the example's content-protection test, but new paid model runs are disabled on Cloud. No OpenAI key is needed. Uploaded inputs do not have shared persistent editing.

Code review is in [draft PR #5](https://github.com/joeywze/research-write-refine-track3/pull/5), targeting `stage-b-development`. The source and interface passed 123 local checks; hosted execution has not yet been verified. Once deployed, share the working app URL in the PR so the team can review both code and behaviour.

Streamlit's [GitHub access requirements](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account) explain the admin requirement. Public submission links remain a separate team decision; do not change the repository or app audience as part of private team review.
