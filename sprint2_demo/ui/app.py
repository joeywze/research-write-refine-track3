"""Choose a research project, read its draft and inspect checked revisions."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import streamlit as st
import core
import jobs
import research
import detection_view

EXAMPLE = "Explore the example project"
UPLOAD = "Upload your research project"

st.set_page_config(page_title="Research Write Refine", page_icon=":material/edit_document:",
                   layout="wide", initial_sidebar_state="collapsed")


@st.cache_data(max_entries=12, ttl=60)
def saved_run(name):
    return core.open_run(name)


def go(stage):
    st.session_state["stage"] = stage


def select_project():
    st.session_state["project_mode"] = st.session_state["_project_choice"]


def open_finished(name):
    saved_run.clear()
    st.session_state["pending_run_id"] = name


def counts(data):
    st.dataframe(core.comparison_rows(data), hide_index=True,
        alt="Rule-based and LLM review-point counts before and after refinement.",
        column_config={"Before refinement": st.column_config.NumberColumn(format="%d"),
                       "After refinement": st.column_config.NumberColumn(format="%d")})
    st.caption("Lower counts mean fewer flagged review points. The two methods may flag the same passage; these are not quality percentages.")
    if not data["summary"]:
        st.caption("Blank values mean the review has not run yet. LLM writing review runs when refinement begins.")
    else:
        st.caption("After refinement refers to the final accepted draft. Unchanged paragraphs keep their previous LLM assessment.")


@st.fragment(run_every="2s")
def live_control(project=None):
    st.subheader("Refine your draft")
    allowed = jobs.live_allowed(st.get_option("server.address"))
    active_id = st.session_state.get("job_id")
    active = jobs.progress(active_id) if active_id else None
    busy = bool(active and active["status"] == "RUNNING")
    if not allowed:
        st.info("New refinement is unavailable in this preview. You can explore the example’s saved results.")
    st.caption("Reviews the original draft and revises flagged passages automatically, with up to three attempts. Changes must pass the content checks before they are kept.")
    if st.button("Refine draft", icon=":material/auto_fix_high:", type="primary", key="start_live", disabled=not allowed or busy):
        try:
            st.session_state["job_id"] = jobs.start_live(st.get_option("server.address"), project)
            st.rerun(scope="fragment")
        except (ValueError, RuntimeError) as error:
            st.error(str(error))
    if active:
        if active["status"] == "RUNNING":
            with st.status("Refinement is running", expanded=True):
                for marker in active["stage_markers"]:
                    st.caption(marker.split(". Estimated budget", 1)[0])
            st.caption("Keep the local demo window open. You can browse the other steps while it works.")
        elif active["status"] == "COMPLETED":
            st.success("Refinement finished. Review the changes and download the result.")
            if st.button("Open completed result", key="open_live"):
                open_finished(active["run_name"])
                st.rerun()
        else:
            st.warning("Refinement stopped. Your previous accepted draft is still available.")


st.session_state.setdefault("stage", "Research")
st.session_state.setdefault("job_id", None)
st.session_state.setdefault("project_mode", EXAMPLE)
if st.session_state["project_mode"] not in {EXAMPLE, UPLOAD}:
    st.session_state["project_mode"] = EXAMPLE
runs = core.available_runs()
if st.session_state.get("pending_run_id"):
    finished = st.session_state.pop("pending_run_id")
    if finished in runs:
        st.session_state["run_id"] = finished
        st.session_state["project_mode"] = EXAMPLE
    else:
        st.session_state["uploaded_result"] = finished
        st.session_state["project_mode"] = UPLOAD
    st.session_state["stage"] = "Results"
if runs:
    st.session_state.setdefault("run_id", core.DEFAULT_RUN if core.DEFAULT_RUN in runs else runs[0])
    if st.session_state["run_id"] not in runs:
        st.session_state["run_id"] = runs[0]
    with st.sidebar:
        st.subheader("Previous example results")
        st.selectbox("Choose a saved refinement", runs, key="run_id")
        st.caption("Includes earlier attempts where no changes were kept.")

st.caption("DSS5105 · TRACK 3 · SPRINT 2")
st.title("Research Write Refine")
st.markdown("Develop a grounded paper and refine its writing while protecting its content.")
if st.session_state["stage"] == "Research":
    detection_view.intro()
detection_view.about()
st.segmented_control("Your workspace", ["Research", "Draft", "Refine", "Results", "Detect"], key="stage", required=True,
                     width="stretch", label_visibility="collapsed")

if st.session_state["stage"] == "Detect":
    detection_view.show()
    st.stop()

if st.session_state["stage"] == "Research":
    st.header("Explore the research proposal")
    st.caption("Prepared from a literature review. Explore the proposed gap and supporting evidence, then continue to the draft.")
    with st.expander("Use another prepared project", expanded=st.session_state["project_mode"] == UPLOAD):
        st.session_state["_project_choice"] = st.session_state["project_mode"]
        mode = st.radio("Project to open", [EXAMPLE, UPLOAD], key="_project_choice", on_change=select_project,
                        format_func=lambda value: "Prepared proposal" if value == EXAMPLE else "Upload another project")
        if mode == UPLOAD:
            st.markdown("Upload the research package and its matching six-section draft. The package contains the research question, claims and supporting evidence.")
            with st.container():
                st.caption("Use schema 0.1 JSON files: research_package.json and v0.json. Each file can be up to 1 MB; drafts can contain up to 60 content blocks and 12,000 words. Uploading checks the format, linked claims and citations; it does not verify that the research is correct.")
                for name, label in (("research_package.json", "Download example research package"), ("v0.json", "Download example draft")):
                    st.download_button(label, (core.ROOT / "inputs/converted" / name).read_bytes(), file_name=name,
                                       mime="application/json", key="example_" + name)
            package_file = st.file_uploader("Research package", type=["json"], key="package_upload", max_upload_size=1)
            draft_file = st.file_uploader("Matching draft", type=["json"], key="draft_upload", max_upload_size=1)
            if st.button("Check and open project", key="check_upload", type="primary", disabled=package_file is None or draft_file is None):
                try:
                    checked = core.uploaded_project(package_file.getvalue(), draft_file.getvalue())
                    st.session_state["uploaded_project"] = checked
                    st.session_state.pop("uploaded_result", None)
                    st.session_state["upload_error"] = None
                    st.success("The files match and include all six sections. Your project is ready to review.")
                except (ValueError, TypeError, KeyError) as error:
                    st.session_state["upload_error"] = str(error)
            if st.session_state.get("upload_error"):
                st.error("The new files could not be opened: " + st.session_state["upload_error"])
            st.caption("Files stay in this browser session until you start a local refinement, which saves them with that run. They are not added to the shared example.")

uploaded = st.session_state["project_mode"] == UPLOAD
if uploaded:
    data = st.session_state.get("uploaded_project")
    if data is None:
        st.info("Choose your research package and matching draft in Research to continue.")
        st.button("Go to Research", on_click=go, args=("Research",))
        st.stop()
    if st.session_state.get("uploaded_result"):
        try:
            result = core.open_run(st.session_state["uploaded_result"])
            if (core.digest(result["package"]) == core.digest(data["package"]) and core.digest(result["drafts"]["v0_input"]) == core.digest(data["drafts"]["v0_input"])):
                data = result
            else:
                st.warning("The previous result belongs to a different project. Your current upload has no refinement result yet.")
        except (OSError, ValueError, KeyError):
            st.warning("The refinement result could not be opened. Your uploaded draft is still available.")
else:
    if not runs:
        st.error("The example’s saved results are unavailable. Upload a research project in Research to continue.")
        st.stop()
    try:
        data = saved_run(st.session_state["run_id"])
    except (OSError, ValueError, KeyError):
        st.error("This saved result could not be opened. Choose another result in the sidebar.")
        st.stop()

package, manifest = data["package"], data["manifest"]
st.badge("Viewing saved results" if data["summary"] else "Uploaded project · not yet refined",
         icon=":material/history:" if data["summary"] else ":material/upload_file:", color="blue")
st.caption("Proposed study — no experimental results" if package.study_status == "proposed" else "Study marked as completed in the supplied package; not independently verified.")

if st.session_state["stage"] == "Research":
    try:
        research.show(data, uploaded=uploaded)
    except (OSError, ValueError, KeyError):
        st.error("The research display could not be matched to the prepared package. Its saved draft is still available.")
    st.button("Continue to draft", icon=":material/arrow_forward:", type="primary", key="to_draft", on_click=go, args=("Draft",))

elif st.session_state["stage"] == "Draft":
    st.header("Review your draft")
    st.caption("Original draft · All six sections")
    section = st.selectbox("Read a section", ["all", *core.SECTIONS], format_func=lambda x: "Whole paper" if x == "all" else core.SECTIONS[x], key="draft_section")
    if section == "all":
        with st.container(height=580, border=True):
            st.markdown(core.paper(data, "v0_input"))
    elif section in core.SECTIONS:
        for p in data["drafts"]["v0_input"].paragraphs:
            if p.section == section:
                st.markdown(core.citation_links(p.text, package))
    with st.container(horizontal=True):
        st.download_button("Download original draft", core.paper(data, "v0_input").encode("utf-8"), file_name="original_v0.md", mime="text/markdown", key="download_v0", icon=":material/download:")
        st.button("Continue to refinement", type="primary", key="to_refine", on_click=go, args=("Refine",))

elif st.session_state["stage"] == "Refine":
    st.header("Review the changes")
    counts(data)
    if data["summary"]:
        st.subheader("What was flagged in the original draft")
        st.caption("See what was flagged, what changed and which changes were kept.")
        items = core.findings(data)
        rule_names = {"LONG_SENTENCE": "Long sentence", "REPEATED_TRANSITIONS": "Repeated linking phrases", "UNIFORM_LENGTH": "Similar sentence lengths"}
        for block in data["initial"]["paragraphs"]:
            for point in block["issues"]:
                with st.expander(core.paragraph_label(data, block["paragraph_id"]) + " · " + rule_names[point["code"]]):
                    st.caption("Rule-based check")
                    st.markdown(point["advice"])
        for index, item in enumerate(items):
            with st.expander(core.paragraph_label(data, item["paragraph_id"]) + " · " + core.point_label(item), expanded=index == 0):
                st.caption("LLM writing review")
                st.markdown(core.citation_links(item["explanation"], package))
                st.markdown("**Suggested change:** " + core.citation_links(item["safe_action"], package))
                st.caption("Original passage")
                st.markdown(core.citation_links(item["quote"], package))
        for change in core.changes(data):
            with st.container(border=True):
                st.subheader(core.paragraph_label(data, change["paragraph_id"]))
                cols = st.columns(2, gap="large")
                with cols[0]:
                    st.caption("Original wording")
                    st.markdown(core.citation_links(change["before"], package))
                with cols[1]:
                    st.caption("Revised wording")
                    st.markdown(core.citation_links(change["after"], package))
                with st.expander("Highlight changed words"):
                    st.markdown(core.marked_diff(change["before"], change["after"]))
        if not core.changes(data):
            st.info("No guided changes were kept. The final draft is the original draft.")
        for attempt in data["summary"]["results"]["guided"]["attempts"]:
            state = "Changes kept" if attempt["accepted"] else "Changes not kept"
            st.markdown(f"**Attempt {attempt['attempt']}: {state}** — {core.stop_explanation(attempt['reason'])}")
            if attempt.get("review_responses"):
                with st.expander("How each review point was addressed"):
                    for response in attempt["review_responses"]:
                        st.markdown(response["explanation"])
    live_control(data if uploaded else None)
    st.button("Continue to results", on_click=go, args=("Results",))

elif st.session_state["stage"] == "Results":
    st.header("Compare and download drafts")
    if not data["summary"]:
        st.info("This project has not been refined yet. Your original draft is available in Draft.")
        st.button("Go to refinement", on_click=go, args=("Refine",))
        st.stop()
    rows = core.score_rows(data)
    for row, label in zip(rows, ("Original draft", "Generic rewrite", "Guided rewrite")):
        row["Version"] = label
    st.dataframe(rows, hide_index=True, alt="Separate rule and LLM review-point counts for original, generic and guided drafts.")
    st.caption("The generic rewrite receives a general writing instruction; the guided rewrite receives the review findings. Both start from the original draft. Blank values mean no assessment is available.")
    guided = data["summary"]["results"]["guided"]
    accepted = [a for a in guided["attempts"] if a["accepted"]]
    if accepted:
        st.success(f"{len(accepted)} guided revision accepted. {core.stop_explanation(guided['stop_reason'])}")
    else:
        st.info("No guided revision was accepted. The final draft is the original draft. " + core.stop_explanation(guided["stop_reason"]))
    st.caption("Zero means no remaining review points under these checks. It does not establish writing quality. Independent reader ratings and evaluation on unseen papers are still pending.")
    detection_view.stage_b_comparison(data)
    with st.container(horizontal=True):
        st.download_button("Download Stage B draft (V2)", core.paper(data, "guided_final").encode("utf-8"), file_name="accepted_guided_v2.md", mime="text/markdown", key="download_guided", type="primary", icon=":material/download:")
        st.download_button("Download generic rewrite", core.paper(data, "generic_final").encode("utf-8"), file_name="generic_v1.md", mime="text/markdown", key="download_generic")
    with st.expander("Read the Stage B draft (V2)"):
        st.markdown(core.paper(data, "guided_final"))
    if not uploaded:
        st.subheader("Try the content-protection check")
        st.markdown("Try changing the planned pilot size from **20 to 21**. Will the app keep the original study detail?")
        st.caption("This test deliberately inserts a wrong number; it was not produced by the writer.")
        if st.button("Test a change to a study detail", icon=":material/verified_user:", key="run_safety"):
            try:
                st.session_state["safety_" + data["name"]] = core.number_challenge(data)
            except (ValueError, StopIteration, OSError):
                st.error("The test could not complete. Your saved draft has not been replaced.")
        safety = st.session_state.get("safety_" + data["name"])
        if safety:
            st.success("The changed number was rejected. The accepted draft was kept unchanged.")
            st.markdown(core.marked_diff(safety["before"], safety["candidate"]))
            with st.expander("Technical test record"):
                st.json(safety)
    st.button("Continue to AI-likeness check", icon=":material/arrow_forward:", type="primary",
              key="to_detect", on_click=go, args=("Detect",))
    with st.expander("Technical details and limitations"):
        st.caption("Saved result: " + data["name"])
        st.json({"models": {k: data["configuration"].get(k) for k in ("writer_model", "preservation_model", "critic_model")},
                 "prompt_version": data["configuration"]["prompt_version"], "usage": core.usage(data),
                 "source_approval": "not independently verified" if uploaded else "pending",
                 "independent_reader_and_unseen_paper_evaluation": "pending"})
        st.caption("Costs use recorded tokens at saved standard rates. Unknown usage, taxes and other applications are separate. Unchanged paragraphs retain their previous style findings; effects on surrounding passages need separate assessment.")
