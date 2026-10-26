"""Display the prepared research and its existing claim-to-evidence records."""
from collections import Counter
import csv
from pathlib import Path

import streamlit as st
import core

CONTEXT = Path(__file__).with_name("research_context.json")
LABELS = {"SUPPORTED": "Supported", "PARTIALLY_SUPPORTED": "Partially supported",
          "PROVISIONALLY_SUPPORTED": "Provisionally supported", "INSUFFICIENT_EVIDENCE": "Insufficient evidence"}


def prepared_context(data):
    context = core.load(CONTEXT)
    if context["schema_version"] != 1 or context["package_hash"] != core.digest(data["package"]):
        raise ValueError("The research display belongs to a different prepared package.")
    path = core.ROOT / "inputs/source/draft_v0_pilot_verification.csv"
    pilot = list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))
    findings = context["pilot_findings"]
    if len(findings) != len(pilot):
        raise ValueError("The displayed findings do not match the saved pilot.")
    for finding, row in zip(findings, pilot):
        ids = [part.strip() for part in row["supporting_evidence_ids"].split(";")]
        if (finding["finding_id"], finding["claim"], finding["paper_id"], finding["status"],
            [e["evidence_id"] for e in finding["evidence"]]) != (
                row["draft_claim_id"], row["draft_claim"], row["paper_id"], row["verification_status"], ids):
            raise ValueError("A displayed claim, support label or evidence link changed.")
        if finding["status"] not in LABELS or not finding["evidence"]:
            raise ValueError("A finding needs its recorded support label and evidence.")
    return context


def pilot_counts(context):
    counts = Counter(f["status"] for f in context["pilot_findings"])
    supported = counts["SUPPORTED"]
    return len(context["pilot_findings"]), supported, len(context["pilot_findings"]) - supported


def uploaded_findings(data):
    """Use only the uploaded package's mappings; never borrow the pilot's labels."""
    package = data["package"]
    evidence = {e.evidence_id: e for e in package.evidence}
    sources = {s.source_id: s for s in package.sources}
    return [{"finding_id": claim.claim_id, "claim": claim.text, "status": None,
        "source_category": "Uploaded literature", "title": "",
        "evidence": [{"quote": evidence[eid].excerpt, "location": evidence[eid].locator,
                      "passage_url": sources[evidence[eid].source_id].url,
                      "title": sources[evidence[eid].source_id].title,
                      "source_kind": next(p["source_kind"] for p in data["manifest"]["evidence_provenance"] if p["evidence_id"] == eid)}
                     for eid in claim.evidence_ids]}
        for claim in package.claims if claim.kind != "proposal" and claim.evidence_ids]


def show_evidence(data, context):
    st.subheader("Check the supporting evidence")
    findings = context["pilot_findings"] if context else uploaded_findings(data)
    if not findings:
        st.info("This package has no evidence-linked literature findings to display.")
        return
    by_id = {f["finding_id"]: f for f in findings}
    st.caption("Choose one of the 7 draft findings in the saved pilot review." if context else
               "These findings use the uploaded package’s claim-to-evidence links. No support labels have been assigned here.")
    selected = st.selectbox("Choose a finding to inspect", list(by_id),
        format_func=lambda key: by_id[key]["claim"], key="research_finding")
    if selected not in by_id:
        return
    finding = by_id[selected]
    with st.container(border=True):
        st.markdown("**Finding:** " + finding["claim"])
        if finding["title"]:
            st.markdown("**Paper:** " + finding["title"])
        st.caption(finding["source_category"])
        if finding["status"]:
            st.badge("Source check: " + LABELS[finding["status"]],
                     color="green" if finding["status"] == "SUPPORTED" else "orange")
            st.caption("Saved pilot review; covers this claim only.")
        else:
            st.caption("Source check: not recorded for this upload.")
        interpretations = []
        for index, evidence in enumerate(finding["evidence"]):
            is_context = evidence.get("source_kind", "").startswith("reviewer_context")
            st.markdown("**Recorded interpretation:**" if is_context else "**Source passage:**")
            quote = evidence["quote"].strip('“”"')
            st.markdown(quote if is_context else "> " + quote.replace("\n", "\n> "))
            if evidence.get("title"):
                st.caption(evidence["title"])
            st.caption("Page " + str(evidence["page"]) if "page" in evidence else evidence["location"])
            if evidence.get("passage_review") == "Not verified":
                st.caption("This passage’s source record is marked “Not verified”.")
            st.link_button("Open paper at this passage" if "page" in evidence else "Open paper",
                           evidence["passage_url"], icon=":material/open_in_new:")
            if evidence.get("interpretation") and evidence["interpretation"] not in interpretations:
                interpretations.append(evidence["interpretation"])
        st.markdown("**How this finding informs the proposal**")
        if interpretations:
            for interpretation in interpretations:
                st.markdown(interpretation)
        else:
            st.caption("A proposal-specific interpretation was not recorded for this finding.")
    st.caption("Passages and review labels come from the prepared records. Use the paper links to check the original source.")


def show(data, uploaded=False):
    package = data["package"]
    context = None if uploaded else prepared_context(data)
    if context:
        st.badge("Provisional proposal · research-team review pending", color="orange")
        st.subheader("How this proposal was developed")
        st.caption("Research preparation takes place before this demo. Some evidence checks and research-team approval remain open.")
        st.mermaid_chart('''flowchart LR
    A["Collect literature<br/>1,809 papers"] --> B["Group topics<br/>19 groups"]
    B --> C["Choose focus<br/>Cluster 7 · 18 papers"]
    C --> D["AI-assisted review<br/>Findings and gaps"]
    D --> E["Review evidence<br/>Checks still open"]
    E --> F["Prepare handover<br/>Research + draft"]''',
            width="stretch", alt="Research preparation: 1,809 papers grouped into 19 topics; Cluster 7 has 18 papers; AI-assisted review and evidence review lead to the provisional research package and draft.")
        st.caption("284 papers were left unassigned. Clustering groups related papers; the later literature review develops and checks the candidate gap.")
        cols = st.columns(2)
        cols[0].metric("Papers in the selected topic", len(context["selected_papers"]), border=True)
        cols[1].metric("Papers cited in this draft", len({p["paper_id"] for p in data["manifest"]["evidence_provenance"]}), border=True)
    else:
        st.info("This uploaded project has passed file-format checks. Its research claims and supporting evidence have not been independently verified here.")
    st.subheader("Proposed research gap")
    st.markdown(package.title)
    st.markdown(package.gap)
    with st.expander("Research questions and proposed contribution"):
        st.markdown("**Research questions**")
        st.markdown(package.research_question)
        st.markdown("**What this study aims to add**")
        st.markdown(package.contribution)
    show_evidence(data, context)
    st.subheader("Checks still open")
    if context:
        total, supported, pending = pilot_counts(context)
        st.warning(f"The saved pilot checked {total} draft claims: {supported} supported; {pending} need further review.")
        st.caption("This is a pilot sample, not a complete fact check of the paper.")
        with st.expander("Findings that need further review"):
            for finding in context["pilot_findings"]:
                if finding["status"] != "SUPPORTED":
                    st.markdown("**" + LABELS[finding["status"]] + "** — " + finding["claim"])
    with st.expander("Research decisions still to be resolved"):
        for unknown in package.unknowns:
            st.markdown("- " + unknown)
    with st.expander("Preparation details"):
        if context:
            st.markdown("**Methods:** " + context["embedding_model"] + " embeddings; " + " + ".join(context["grouping_methods"]) + ".")
            st.caption("Topic names and the research focus are reviewed after grouping. Literature extraction and candidate-gap assessment use AI assistance. These are separate preparation steps, not tasks started from this screen.")
            st.markdown("**Papers in the selected topic**")
            for paper in context["selected_papers"]:
                st.link_button(paper["title"], paper["paper_url"])
            st.caption("Research source revision: " + context["source_revision"])
            st.json({"source_files": context["source_files"], "pilot_scope": context["pilot_scope"]})
        else:
            st.caption("Uploaded source records and locations")
            for evidence in package.evidence:
                st.caption(evidence.evidence_id + " · " + evidence.locator)
