# Sprint 2 preview

The current preview is deployed from `tangh86/research-write-refine-track3`, branch `UI-demo`, with entrypoint `sprint2_demo/ui/app.py`. Local checks use Python 3.12; the existing Cloud deployment reports Python 3.14.9. Leave Secrets empty: the preview uses saved outputs and blocks new paid model runs.

[Open the preview](https://7re4qdfrjans8utyap8rch.streamlit.app/).

The team copy is on `joeywze/research-write-refine-track3`, branch `sprint2-ui-demo`, in [draft PR #5](https://github.com/joeywze/research-write-refine-track3/pull/5) against `stage-b-development`. Updating the fork preview does not require a merge into either development or main.

## What to check

1. Research opens the prepared proposal and explains the preparation workflow. There are 18 papers in the selected topic and 7 cited in the draft.
2. Choose a finding to see its passage, original source link and saved support label in one place. The pilot covers 7 claims: 3 supported and 4 needing further review. It is not a complete fact check.
3. Open Draft, then Refine. In the saved example, rules stay at 0 and LLM review points fall from 2 to 0. These counts are internal diagnostics, not independent quality ratings.
4. Run the study-detail change test and confirm the injected number change is rejected. Download the refined draft.
5. To inspect another prepared package, use **Use another prepared project**. Uploads do not inherit the example's support labels or scores.

The preview has no shared persistent editing of uploaded inputs. Changes to app source are made in GitHub; access to view the app and access to edit code are separate. Keep the current audience unless the team agrees otherwise.

## Deploy another copy

Use the repository, branch and entrypoint above, or an authorised team administrator can deploy `joeywze/research-write-refine-track3` at `sprint2-ui-demo`. See the official [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy). No OpenAI key is needed for this preview.

The Research interface and record checks passed 20 offline tests. Browser verification is recorded separately under `verification/stage_a_research_view.json`. Research-team approval, held-out evaluation and independent human ratings remain pending.
