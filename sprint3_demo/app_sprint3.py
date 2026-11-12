"""Sprint 3 demo site, built on the Sprint 2 site's look and components.

Changes from Sprint 2: a four-step walkthrough over all five topics (Build the paper: 1 Choose a topic,
2 First draft; Polish the writing: 3 Rewrite, 4 Compare), claim review that can hold paragraphs, and a
box to score and rewrite your own text. The Sprint 2 detector pages are kept as "Detector and tests".

Everything in the walkthrough comes from saved runs (sprint3_demo/bundles, made by build_demo_bundles.py),
so the hosted site needs no API key. Rewriting your own text runs only in the local version:
    set TRACK3_LOCAL_LIVE=1 (and OPENAI_API_KEY), then  streamlit run sprint3_demo/app_sprint3.py
The Sprint 2 site (sprint2_demo/ui/app.py) is unchanged.
"""

import os
from pathlib import Path
import sys

import streamlit as st

HERE = Path(__file__).resolve().parent
UI2 = HERE.parent / "sprint2_demo" / "ui"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(UI2))
import importlib  # noqa: E402
import demo_logic as d  # noqa: E402
d = importlib.reload(d)  # pick up edits to demo_logic.py without restarting Streamlit
import look  # noqa: E402  (Sprint 2 styles and components)
import detection_view as dv  # noqa: E402  (Sprint 2 detector pages)

st.set_page_config(page_title="Research Write Refine", page_icon=":material/edit_document:",
                   layout="wide", initial_sidebar_state="collapsed")

STEPS = {1: ":material/travel_explore: 1 · Choose a topic", 2: ":material/article: 2 · First draft",
         3: ":material/auto_fix_high: 3 · Rewrite", 4: ":material/compare_arrows: 4 · Compare"}
RAW_GPT = 61.0   # Sprint 2 reference: raw GPT paragraphs
WRITER = os.environ.get("HALF2_WRITER_MODEL", "gpt-5.4-mini-2026-03-17")
EXTRA_CSS = f"""
<style>
.rw-groups {{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:.4rem 0 -.2rem;font-size:.85rem;font-weight:700;color:{look.MUTED}}}
.rw-groups div {{border-bottom:3px solid {look.LINE};padding-bottom:4px}}
.rw-groups div.on {{border-bottom-color:{look.HUMAN};color:{look.INK}}}
.st-key-rw_nav {{position:fixed;bottom:18px;right:28px;z-index:999;background:{look.PAPER};border:1px solid {look.LINE};
  border-radius:12px;padding:8px 10px;box-shadow:0 6px 18px rgba(30,42,68,.12);width:auto !important}}
.rw-del {{background:#FBE3E3;color:#8E2A2A;text-decoration:line-through}}
.rw-ins {{background:#DDF3EC;color:{look.HUMAN};text-decoration:none}}
.rw-tag {{font-size:.8rem;font-weight:700;padding:2px 9px;border-radius:99px;display:inline-block;margin:0 6px 4px 0;
  border:1px solid currentColor}}
</style>
"""
OUTCOME_COLOURS = {"Rewritten": look.HUMAN, "Kept unchanged": look.MUTED, "Held, needs research": look.MID,
                   "Held, needs revision": look.MID}


# ---------------------------------------------------------------- the scale (Sprint 2 style, labels never overlap)
def meter(points, caption):
    """Sprint 2's gradient meter. Labels that would collide are stacked on extra rows."""
    from html import escape
    points = [(lb, float(sc), k) for lb, sc, k in points if sc is not None]
    rows = {}
    for side in ("up", "down"):
        last = []          # right edge (in score units) of the last label on each row
        for lb, sc, k in sorted([p for p in points if p[2] == side], key=lambda p: p[1]):
            half = (len(f"{lb} · {sc:.0f}") * 0.55) / 2     # rough label half-width in scale units
            row = next((i for i, edge in enumerate(last) if sc - half > edge + 1), len(last))
            if row == len(last):
                last.append(0)
            last[row] = sc + half
            rows[(lb, sc)] = row
    marks = []
    for lb, sc, k in points:
        s_ = max(0.0, min(100.0, sc))
        row = rows[(lb, sc)]
        cls = "mark up" if k == "up" else "mark down ref"
        dot = f'style="background:{look.tone(s_)}"' if k == "up" else ""
        offset = f"bottom:{24 + 20 * row}px" if k == "up" else f"top:{22 + 20 * row}px"
        marks.append(f'<div class="{cls}" style="left:{s_:.1f}%"><span class="dot" {dot}></span>'
                     f'<span class="lab" style="{offset}">{escape(lb)} · {s_:.0f}</span></div>')
    up_rows = 1 + max([r for (lb, sc), r in rows.items() if any(p[0] == lb and p[2] == "up" for p in points)] or [0])
    down_rows = 1 + max([r for (lb, sc), r in rows.items() if any(p[0] == lb and p[2] == "down" for p in points)] or [0])
    st.html(f'''<div class="rw-meter" role="img" aria-label="{escape(caption)}">
  <div class="cap" style="margin-bottom:{2.4 + 1.25 * (up_rows - 1):.2f}rem">{escape(caption)}</div>
  <div class="track">{"".join(marks)}</div>
  <div class="ends" style="margin-top:{2.3 + 1.25 * (down_rows - 1):.2f}rem"><span><b class="h">0 · reads like a real paper</b></span>
  <span>40-60 borderline</span><span><b class="m">100 · reads like an LLM</b></span></div>
</div>''')


# ---------------------------------------------------------------- state and navigation
def state():
    s = st.session_state
    for k, v in {"step": 1, "topic": None, "review_mode": None, "decisions": {}, "focus": None}.items():
        s.setdefault(k, v)
    return s


def go(step):
    st.session_state.step = step


def progress_bar(s):
    group = "Build the paper" if s.step <= 2 else "Polish the writing"
    st.html(f'<div class="rw-groups"><div class="{"on" if group == "Build the paper" else ""}">Build the paper</div>'
            f'<div class="{"on" if group == "Polish the writing" else ""}">Polish the writing</div></div>')
    st.segmented_control("Steps", list(STEPS), key="step", required=True, format_func=STEPS.get,
                         width="stretch", label_visibility="collapsed")


def nav_buttons(s):
    """Back / Next, fixed at the bottom right of the window so nobody has to scroll for them."""
    with st.container(key="rw_nav", horizontal=True):
        if s.step > 1:
            st.button("Back", icon=":material/arrow_back:", on_click=go, args=(s.step - 1,), key="nav_back")
        if s.step < 4:
            label = {1: "Draft the paper", 2: "Polish the writing", 3: "Compare"}[s.step]
            blocked = s.step == 1 and not ready_to_draft(s)
            st.button(label, icon=":material/arrow_forward:", type="primary", on_click=go, args=(s.step + 1,),
                      key="nav_next", disabled=blocked,
                      help="Choose a topic, then review its claims or proceed without reviewing." if blocked else None)


def ready_to_draft(s):
    if not s.topic:
        return False
    b = d.bundle(s.topic)
    if b["reviewed"] or s.review_mode == "skip":
        return True
    return s.review_mode == "review" and all(c["claim_id"] in s.decisions for c in b["claims"])


def current_view(s):
    b = d.bundle(s.topic)
    held = d.held_by_user(b, s.decisions, s.review_mode == "review")
    paragraphs, records = d.final_view(b, held)
    return b, held, paragraphs, records


# ---------------------------------------------------------------- introduction (as on the Sprint 2 site)
def welcome(s):
    with st.expander("Start here: what this site does and how to use it", expanded=s.step == 1 and not s.topic,
                     icon=":material/explore:"):
        st.markdown("**The problem.** Research papers drafted with an LLM have a recognisable style: stacked hedges "
                    "(*may potentially suggest*), lists of three, every sentence the same length, stock phrases. "
                    "Readers notice it, and a careless rewrite can quietly change the facts.")
        st.markdown("**Who it's for.** Researchers and students who draft with an LLM and want the paper grounded "
                    "in real literature and readable as human writing, without its facts changing.")
        firsts = [d.bundle(t["id"])["v0"]["mean"] for t in d.topics()]
        finals = [d.bundle(t["id"])["final"]["mean"] for t in d.topics()]
        meter([("First drafts", d.mean(firsts), "up"), ("Final papers", d.mean(finals), "up"),
                    ("Real EMNLP abstracts", d.ALL_EMNLP_MEAN, "down"), ("Raw GPT text", RAW_GPT, "down")],
                   "Where our five papers started and finished on the detector's scale (averages)")
        st.markdown("**How to use the site.** Go through the four steps in the bar below, left to right. "
                    "You can click any step to jump to it; Back and Next stay at the bottom right of the window.")
        st.mermaid_chart('''flowchart LR
    subgraph B["Build the paper"]
    A["1 · Choose a topic<br/>gap from EMNLP 2025 papers,<br/>check its claims"] --> C["2 · First draft<br/>six sections,<br/>scored paragraph by paragraph"]
    end
    subgraph P["Polish the writing"]
    D["3 · Rewrite<br/>detector-guided,<br/>facts checked"] --> E["4 · Compare<br/>score before and after,<br/>download"]
    end
    C --> D''', width="stretch",
                         alt="Four steps: choose a topic, first draft, rewrite, compare.")
        st.markdown("Two more pages sit in the top menu: **Score and rewrite your text** (paste a paragraph or "
                    "upload a paper) and **Detector and tests** (how the detector works and how we tested it).")
        st.caption("Everything in the walkthrough is a saved run of the real system. Rewriting new text needs an "
                   "API key, so it is switched off in this online preview.")


# ---------------------------------------------------------------- step 1
def step_topic(s):
    st.header(":material/travel_explore: Choose a research topic")
    look.guide("How to use this page", [
        "Each card is a research topic with the **gap** our research stage found in EMNLP 2025 papers.",
        "Select one to see its research question and contribution.",
        "Four topics were mapped to sources automatically: **review their claims** against the source quotes, or "
        "proceed without reviewing. Claims you mark *Needs revision* keep their paragraphs from being rewritten."],
        "🔎")
    topics = d.topics()
    cols = st.columns(len(topics))
    for col, t in zip(cols, topics):
        with col.container(border=True):
            colour = look.HUMAN if t["reviewed"] else look.MID
            st.html(f'<span class="rw-tag" style="color:{colour}">{t["status_label"]}</span>')
            st.markdown(f"**{t['title']}**")
            st.caption("Gap: " + t["gap"][:200] + ("…" if len(t["gap"]) > 200 else ""))
            if st.button("Selected" if s.topic == t["id"] else "Select", key=f"pick_{t['id']}",
                         type="primary" if s.topic == t["id"] else "secondary", width="stretch"):
                s.topic, s.review_mode, s.decisions, s.focus = t["id"], None, {}, None
                clear_widgets()
                st.rerun()
    if not s.topic:
        st.info("Select a topic to continue.")
        return
    b = d.bundle(s.topic)
    with st.container(border=True):
        st.subheader(b["title"])
        st.markdown(f"**Research question.** {b['research_question']}")
        st.markdown(f"**Research gap.** {b['gap']}")
        st.markdown(f"**Proposed contribution.** {b['contribution']}")
    claims_step(s, b)


def claims_step(s, b):
    st.subheader(":material/fact_check: Check the claims behind this topic")
    if b["reviewed"]:
        st.success("The team has already reviewed this topic's claims against their sources. Continue with "
                   "**Draft the paper**.")
        return
    st.caption(f"{len(b['claims'])} claims were matched to their sources automatically and have not been checked by "
               "a person.")
    c1, c2 = st.columns(2)
    if c1.button("Review the claims", icon=":material/rule:", width="stretch",
                 type="primary" if s.review_mode == "review" else "secondary"):
        s.review_mode = "review"
        st.rerun()
    if c2.button("Proceed without reviewing", icon=":material/skip_next:", width="stretch",
                 type="primary" if s.review_mode == "skip" else "secondary"):
        s.review_mode = "skip"
        st.rerun()
    if s.review_mode == "skip":
        st.info("Claims not reviewed: every selected paragraph can be rewritten, and paragraphs with unchecked claims "
                "will be marked ⚠ in the draft and the rewrite. Continue with **Draft the paper**.")
        return
    if s.review_mode != "review":
        return
    st.button("Approve all claims", icon=":material/done_all:", on_click=approve_all, args=(b,), key="approve_all")
    done = sum(c["claim_id"] in s.decisions for c in b["claims"])
    st.progress(done / max(len(b["claims"]), 1), text=f"{done} of {len(b['claims'])} claims checked")
    for c in b["claims"]:
        with st.container(border=True):
            st.markdown(f"**{c['paragraph_id']}** · {c['claim']}")
            for e in c["evidence"][:2]:
                link = f" · [open the paper]({e['url']})" if e["url"] else ""
                st.caption(f"*{e['title']}*: “{e['quote']}” · {e['page']}{link}")
            choice = st.segmented_control("Decision", ["Approve", "Needs revision"], key=f"claim_{c['claim_id']}",
                                          label_visibility="collapsed")
            if choice:
                s.decisions[c["claim_id"]] = choice
            else:
                s.decisions.pop(c["claim_id"], None)
    held = d.held_by_user(b, s.decisions, True)
    if done < len(b["claims"]):
        st.info(f"Check every claim to continue ({len(b['claims']) - done} left), or choose Proceed without reviewing.")
    elif held:
        st.warning(f"{len(held)} paragraph(s) have a claim that needs revision ({', '.join(sorted(held))}). "
                   "They will be held, not rewritten.")
    else:
        st.success("All claims approved. Continue with **Draft the paper**.")


def approve_all(b):
    for c in b["claims"]:
        st.session_state.decisions[c["claim_id"]] = "Approve"
        st.session_state[f"claim_{c['claim_id']}"] = "Approve"


# ---------------------------------------------------------------- step 2
def unreviewed(s, b):
    """Claims per paragraph that the user skipped reviewing (provisional topics only)."""
    if b["reviewed"] or s.review_mode != "skip":
        return {}
    out = {}
    for c in b["claims"]:
        out.setdefault(c["paragraph_id"], []).append(c)
    return out


def claim_flag(pid, flags):
    """A 'claims not reviewed' tag with the claims and their sources, for one paragraph."""
    claims = flags.get(pid)
    if not claims:
        return
    st.html(f'<span class="rw-tag" style="color:{look.MID}">⚠ {len(claims)} claim{"s" if len(claims) > 1 else ""} '
            f'not reviewed</span>')
    with st.expander(f"Check the claims in {pid} against their sources"):
        for c in claims:
            st.markdown(f"**{c['claim']}**")
            for e in c["evidence"][:2]:
                link = f" · [open the paper]({e['url']})" if e["url"] else ""
                st.caption(f"*{e['title']}*: “{e['quote']}” · {e['page']}{link}")


def paper_view(paragraphs, flags=None):
    flags = flags or {}
    for p in paragraphs:
        text = d.plain(p["text"])
        title = f"{p['id']} · {p['section'].replace('_', ' ')}"
        claim_flag(p["id"], flags)
        if text.lstrip().startswith("|"):
            st.caption(title)
            st.markdown(text)
        else:
            look.paper(title, text, p["score"])


def step_draft(s):
    b = d.bundle(s.topic)
    st.header(":material/article: First draft")
    st.caption("Written by our research stage from the topic's evidence · all six sections · nothing rewritten yet")
    look.guide("How to use this page", [
        "Each paragraph carries its **detector score**: 0 reads like a real paper, 100 like an LLM.",
        "Paragraphs scoring **35 or more** will be rewritten in the next step.",
        "Pick a section to read, or download the whole first draft."], "📄")
    scored = [p for p in b["v0"]["paragraphs"] if p["score"] is not None]
    band = b["real_band"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Whole-paper score", f"{b['v0']['mean']:.0f}", help="Average over the paper's scored paragraphs.")
    m2.metric("Paragraphs to rewrite (35+)", f"{sum(p['score'] >= d.THRESHOLD for p in scored)} of {len(scored)}")
    m3.metric("Real papers it cites", f"{band['mean']:.0f}" if band["n"] else "–",
              help=f"Average score of the abstracts of the {band['n']} cited EMNLP 2025 papers we have.")
    meter([("First draft", b["v0"]["mean"], "up"), ("Real papers it cites", band["mean"], "down"),
                ("Raw GPT text", RAW_GPT, "down")], "Where this first draft sits on the detector's scale")
    flags = unreviewed(s, b)
    if flags:
        st.warning(f"You skipped the claim review: {sum(len(v) for v in flags.values())} claims in "
                   f"{len(flags)} paragraphs were matched to sources automatically and not checked by a person. "
                   "They are marked ⚠ below; open one to check it against its source.")
    sections = list(dict.fromkeys(p["section"] for p in b["v0"]["paragraphs"]))
    pick = st.selectbox("Read a section", ["all", *sections],
                        format_func=lambda x: "Whole paper" if x == "all" else x.replace("_", " ").capitalize())
    with st.container(height=600, border=True):
        paper_view([p for p in b["v0"]["paragraphs"] if pick in ("all", p["section"])], unreviewed(s, b))
    st.download_button("Download first draft", d.render_markdown(b, b["v0"]["paragraphs"]),
                       file_name=f"{b['id']}_first_draft.md", mime="text/markdown", icon=":material/download:")


# ---------------------------------------------------------------- step 3
def step_rewrite(s):
    b, held, paragraphs, records = current_view(s)
    st.header(":material/auto_fix_high: Rewrite")
    st.caption("Detector-guided rewriting · every change checked against the original and the evidence")
    look.guide("How to use this page", [
        "Every paragraph scoring 35 or more got **up to three rewrite attempts**, each told what pushes its score up.",
        "A rewrite is kept only if it lowers the score by **at least 5** and passes **every content check**: "
        "fluency, facts kept, no new facts, evidence and meaning. Otherwise the original stays.",
        "Open **Attempts** on any paragraph to see why a version was rejected, or press **Show hard case**."], "🖊️")
    counts = d.outcome_counts(records)
    m = st.columns(4)
    m[0].metric("Rewritten", counts["revised"])
    m[1].metric("Kept unchanged", counts["kept original"], help="No attempt both lowered the score enough and "
                "passed every check. These are flagged for a human edit.")
    m[2].metric("Held", counts["held for research"] + counts["held by you"],
                help="Held for research by the reviewer, or held because you marked a claim as needing revision.")
    m[3].metric("Average score of these paragraphs",
                f"{d.mean([r['score_before'] for r in records]):.0f} → {d.mean([r['score_after'] for r in records]):.0f}")
    critic = b["rewrite"].get("critic") or {}
    if critic:
        with st.expander("What the independent reviewer said", icon=":material/rate_review:"):
            st.markdown(f"A separate model (`{critic.get('model')}`) reviewed the first draft and the final paper. "
                        f"First-draft review: **{critic.get('review_of_v0')}**; final review: "
                        f"**{critic.get('review_of_final')}**. Wording issues it flagged: "
                        f"{critic.get('actionable_before')} before → {critic.get('actionable_after')} after.")
            for n in critic.get("needs_research") or []:
                st.markdown(f"- **{n['paragraph_id']}** needs research ({n['criterion']}): {n['explanation']}")
    c1, c2 = st.columns([3, 1])
    labels = ["All"] + [lab for k, (lab, _) in d.OUTCOMES.items() if counts[k]]
    show = c1.segmented_control("Show", labels, default="All", key="rw_filter", label_visibility="collapsed")
    hard = d.hard_case(records)
    if hard and c2.button("Show hard case", icon=":material/gavel:", width="stretch"):
        s.focus = hard
    if s.focus:
        st.info(f"Hard case {s.focus}: a content check stopped a fluent rewrite. Open **Attempts** to see why.")
        if st.button("Show all paragraphs"):
            s.focus = None
            st.rerun()
    for r in records:
        label, _ = d.OUTCOMES[r["outcome"]]
        if s.focus and r["paragraph_id"] != s.focus:
            continue
        if not s.focus and show not in (None, "All") and label != show:
            continue
        record_card(b, r, label, unreviewed(s, b))


def record_card(b, r, label, flags=None):
    v0 = {p["id"]: p["text"] for p in b["v0"]["paragraphs"]}
    final = {p["id"]: p["text"] for p in b["final"]["paragraphs"]}
    pid = r["paragraph_id"]
    with st.container(border=True):
        colour = OUTCOME_COLOURS[label]
        st.html(f'<b>{pid}</b> · {r["section"].replace("_", " ")} &nbsp;<span class="rw-tag" style="color:{colour}">'
                f'{label}</span> {look.chip(r["score_before"])} → {look.chip(r["score_after"])}')
        claim_flag(pid, flags or {})
        if r["outcome"] == "revised":
            cols = st.columns(2, gap="large")
            cols[0].caption("First draft")
            cols[0].markdown(d.plain(v0[pid]))
            cols[1].caption("Rewritten")
            cols[1].markdown(d.plain(final[pid]))
            with st.expander("Highlight changed words"):
                st.html(d.word_diff(v0[pid], final[pid]))
            st.caption("Checks passed: " + " · ".join(f"{n} {'✓' if ok else '✗'}" for n, ok in d.accepted_checks(r)))
        else:
            reason = {"held by you": "You marked a claim in this paragraph as needing revision, so it was not rewritten.",
                      "held for research": "The reviewer found a gap that needs new evidence, so it was not rewritten: "
                                           + (r.get("held_reason") or ""),
                      }.get(r["outcome"], "No attempt both lowered the score enough and passed every check, so the "
                                          "original was kept." + (" A person should edit it." if r.get("needs_human_edit") else ""))
            st.caption(reason)
            st.markdown(d.plain(v0[pid]))
        if r["top_features"]:
            st.caption("Why it was selected: " + ", ".join(r["top_features"]))
        if r["attempts"]:
            with st.expander(f"Attempts ({len(r['attempts'])})"):
                for a in r["attempts"]:
                    sc = f" · score {a['score']:.0f}" if a["score"] is not None else ""
                    st.markdown(f"{'✅' if a['accepted'] else '❌'} **Attempt {a['attempt']}**{sc}: "
                                f"{d.plain_verdict(a['verdict'])}")


# ---------------------------------------------------------------- step 4
def step_compare(s):
    b, held, paragraphs, records = current_view(s)
    final_mean = d.mean([p["score"] for p in paragraphs])
    band = b["real_band"]
    st.header(":material/compare_arrows: Compare")
    look.guide("How to use this page", [
        "The scale shows the whole paper before and after rewriting, next to the real papers it cites.",
        "Lower means less formulaic style. It is not proof that a person wrote it: see *How reliable is this score?*",
        "Download the final paper, the change report, and your claim decisions."], "⚖️")
    m1, m2, m3 = st.columns(3)
    m1.metric("First draft", f"{b['v0']['mean']:.0f}")
    m2.metric("Final paper", f"{final_mean:.0f}", delta=f"{final_mean - b['v0']['mean']:.0f}", delta_color="inverse")
    m3.metric("Real papers it cites", f"{band['mean']:.0f}" if band["n"] else "–",
              help=(f"Abstracts of {band['n']} cited EMNLP 2025 papers, range {band['min']:.0f}–{band['max']:.0f}, "
                    "each scored by a detector that never saw it.") if band["n"] else None)
    meter([("First draft", b["v0"]["mean"], "up"), ("Final paper", final_mean, "up"),
                ("Real papers it cites", band["mean"], "down"), ("Raw GPT text", RAW_GPT, "down")],
               "Where this paper started and finished on the detector's scale")
    if held:
        st.caption(f"Includes your holds: {', '.join(sorted(held))} kept their first-draft text.")
    flags = unreviewed(s, b)
    if flags:
        st.warning(f"This paper still has {sum(len(v) for v in flags.values())} claims that nobody has checked "
                   f"against their sources (in {', '.join(sorted(flags))}). Review them before using the paper; "
                   "the claim-decisions download lists them.")
    with st.container(border=True):
        st.markdown("**:material/help: How reliable is this score?**")
        st.markdown("On EMNLP papers it never saw, our detector ranks an AI-written passage above a real one 74% of "
                    "the time (AUC 0.74; 0.5 is guessing). It measures style habits, not authorship. An outside "
                    "detector, GPTZero, still rated our rewritten passages as AI, so read the score as a writing "
                    "guide. Details are in **Detector and tests**.")
    with st.container(horizontal=True):
        st.download_button("Final paper", d.render_markdown(b, paragraphs), file_name=f"{b['id']}_final_paper.md",
                           mime="text/markdown", type="primary", icon=":material/download:")
        st.download_button("Change report", d.change_report(b, records, held), file_name=f"{b['id']}_change_report.json",
                           mime="application/json", icon=":material/download:")
        if b["claims"]:
            st.download_button("Your claim decisions", d.decisions_csv(b, s.decisions, s.review_mode == "review"),
                               file_name=f"{b['id']}_claim_decisions.csv", mime="text/csv", icon=":material/download:")
    with st.expander("Read the final paper"):
        st.markdown(d.render_markdown(b, paragraphs))
    st.button("Start again with another topic", icon=":material/restart_alt:", on_click=reset)


def reset():
    for k in ("topic", "review_mode", "focus"):
        st.session_state[k] = None
    st.session_state.decisions = {}
    clear_widgets()
    st.session_state.step = 1


def clear_widgets():
    for k in [k for k in st.session_state if k.startswith("claim_") or k == "rw_filter"]:
        del st.session_state[k]


# ---------------------------------------------------------------- pages
def walkthrough():
    s = state()
    look.style()
    st.html(EXTRA_CSS)
    look.hero("Research Write Refine",
              "From a research gap in published work to a paper that reads like a person wrote it, "
              "without changing its facts.", "DSS5105 · Track 3 · Group 17")
    welcome(s)
    progress_bar(s)
    if s.step > 1 and not s.topic:
        st.info("Choose a topic in step 1 first.")
        st.button("Go to step 1", on_click=go, args=(1,))
        return
    {1: step_topic, 2: step_draft, 3: step_rewrite, 4: step_compare}[s.step](s)
    nav_buttons(s)


def own_text():
    look.style()
    st.html(EXTRA_CSS)
    st.header(":material/edit_note: Score and rewrite your text")
    allowed, why = d.live_allowed()
    look.guide("How to use this page", [
        "Paste one of your own paragraphs, or upload a paper as Markdown or plain text. This skips *Build the "
        "paper* and goes straight to *Polish the writing*.",
        "You get the detector score and the sentences that sound machine-written.",
        "**Rewrite it** runs the detector-guided rewriter (up to three attempts) with the number, citation and "
        "fluency checks. The evidence and meaning checks need a research package, so they run only on the "
        "prepared topics."], "✨")
    if not allowed:
        st.info(why)
    tab_text, tab_file = st.tabs([":material/edit_note: Paste a paragraph", ":material/upload_file: Upload a paper"])
    with tab_text:
        text = st.text_area("Your paragraph", height=180, key="own_text",
                            placeholder="Paste a paragraph from your own paper here.")
        if not text.strip() or len(text.split()) < 15:
            st.info("Paste at least a sentence or two (15+ words) to score.")
        else:
            a = dv.analysis(text)
            meter([("Your text", a["score"], "up"), ("Real EMNLP abstracts", d.ALL_EMNLP_MEAN, "down"),
                   ("Raw GPT text", RAW_GPT, "down")], f"Score {a['score']:.0f} / 100: {dv.verdict(a['score'])[0].lower()}")
            if a["drivers"]:
                st.markdown("**What pushes the score up:** " + "; ".join(a["drivers"]))
            st.markdown("**Flagged sentences** (highlighted):")
            st.markdown(dv.highlighted(text, a["flagged"]))
            if st.button("Rewrite it", icon=":material/auto_fix_high:", type="primary", disabled=not allowed,
                         key="own_rewrite", help=None if allowed else why):
                with st.spinner("Rewriting, up to three attempts…"):
                    best, sc, log = d.rewrite_text(text, WRITER)
                for i, score, verdict in log:
                    st.caption(f"Attempt {i}: " + (f"score {score:.0f} · " if score is not None else "") + verdict)
                if best:
                    st.success(f"Kept a rewrite: {a['score']:.0f} → {sc:.0f}.")
                    st.markdown(best)
                    with st.expander("Highlight changed words"):
                        st.html(d.word_diff(text, best))
                    st.download_button("Download the rewrite", best, file_name="rewritten_paragraph.txt")
                else:
                    st.warning("No attempt both lowered the score by 5 and passed the checks, so your paragraph stands.")
    with tab_file:
        file = st.file_uploader("Paper (.md or .txt)", type=["md", "txt"], key="own_file")
        if file:
            rows = [(i, p, dv.analysis(d.plain(p))["score"]) for i, p in
                    enumerate(d.split_upload(file.getvalue().decode("utf-8", errors="replace")), 1)]
            if not rows:
                st.warning("No paragraphs of 40 words or more were found.")
            else:
                selected = [r for r in rows if r[2] >= d.THRESHOLD]
                m1, m2 = st.columns(2)
                m1.metric("Whole-paper score", f"{d.mean([r[2] for r in rows]):.0f}")
                m2.metric("Paragraphs that would be rewritten (35+)", f"{len(selected)} of {len(rows)}")
                meter([("Your paper", d.mean([r[2] for r in rows]), "up"),
                       ("Real EMNLP abstracts", d.ALL_EMNLP_MEAN, "down"), ("Raw GPT text", RAW_GPT, "down")],
                      "Where your paper sits on the detector's scale")
                for i, p, sc in rows:
                    look.paper(f"Paragraph {i}", d.plain(p), sc)
                st.caption("To rewrite one of these, paste it into **Paste a paragraph**.")


def detector_page():
    import json
    import pandas as pd
    look.style()
    st.html(EXTRA_CSS)
    st.header(":material/troubleshoot: Detector and tests")
    st.caption("How the detector works, how the rewriting pipeline uses it, and how we tested both, from the final runs.")
    look.guide("How to use this page", [
        "**Try it**: pick one of the example texts and see its score and the sentences that sound machine-written.",
        "**1 · The detector**: what it measures, why we built it this way, and how well it works on unseen papers.",
        "**2 · The rewriting pipeline**: the checks every rewrite must pass, and what happened across all five topics.",
        "**3 · Tests**: planted errors the checks caught, and what an outside detector (GPTZero) said."], "🧪")
    tabs = st.tabs([":material/edit_note: Try it", ":material/troubleshoot: 1 · The detector",
                    ":material/account_tree: 2 · The rewriting pipeline", ":material/fact_check: 3 · Tests"])
    with tabs[0]:
        options = d.example_texts()
        choice = st.selectbox("Example text", list(options), key="det_example")
        text = options[choice]
        a = dv.analysis(text)
        meter([("This text", a["score"], "up"), ("Real EMNLP abstracts", d.ALL_EMNLP_MEAN, "down"),
               ("Raw GPT text", RAW_GPT, "down")], f"Score {a['score']:.0f} / 100: {dv.verdict(a['score'])[0].lower()}")
        cols = st.columns(2)
        cols[0].metric("Hedge words", a["hedges"], help="may, might, could, potentially, suggests ...")
        cols[1].metric("Sentence lengths (words)", ", ".join(map(str, a["lengths"][:8])) or "–",
                       help="Real writing mixes short and long sentences.")
        if a["drivers"]:
            st.markdown("**What pushes the score up:** " + "; ".join(a["drivers"]))
        st.markdown("**The text, with flagged sentences highlighted:**")
        st.markdown(dv.highlighted(text, a["flagged"]))
        for f in a["flagged"][:8]:
            st.caption(f"Sentence {f['index'] + 1}: " + "; ".join(f["reasons"]))
        st.caption("To score your own writing, use **Score and rewrite your text** in the top menu.")
    with tabs[1]:
        st.markdown("#### :material/straighten: What it measures")
        st.markdown("| Signal | What LLM text tends to do |\n|---|---|\n"
                    "| Hedge density | stacks *may, could, potentially, suggests* everywhere |\n"
                    "| Sentence-length variation | keeps every sentence about the same length |\n"
                    "| Long sentences | avoids the long, dense sentences real papers use |\n"
                    "| Stock phrases | *it is important to note, plays a crucial role, these findings highlight* |\n"
                    "| Lists of three | \"robust, scalable, and efficient\" in sentence after sentence |")
        dv.justification()
        st.markdown("#### :material/verified: Does it work on papers it never saw?")
        cv = json.loads((d.ROOT / "results/detection/heldout_eval/grouped_cv.json").read_text(encoding="utf-8"))
        lo, hi = cv["auc_95ci_by_paper"]
        m = st.columns(3)
        m[0].metric("AUC on unseen papers", f"{cv['auc']:.2f}", help=f"95% interval {lo:.2f}-{hi:.2f}. 0.5 = coin flip, 1 = perfect.")
        m[1].metric("Right as a yes/no label at 50", f"{cv['accuracy_at_50']:.0%}")
        m[2].metric("Test set", f"{cv['ai_passages']} AI · {cv['human_papers']:,} real")
        st.markdown(f"Given one real and one AI-written passage from papers it never saw, the detector rates the AI one "
                    f"as more AI-like **{cv['auc']:.0%} of the time** (95% interval {lo:.0%}-{hi:.0%}). Each of the "
                    f"{cv['ai_papers']} AI papers was scored by a version trained without it.")
        auc = pd.DataFrame({"Held-out AI paper": [k.replace("2025.emnlp-main.", "#") for k in cv["per_ai_paper_auc"]],
                            "AUC": list(cv["per_ai_paper_auc"].values())})
        st.bar_chart(auc, x="Held-out AI paper", y="AUC", color=look.HUMAN)
        fx = d.ROOT / "results/detection/feature_effects.csv"
        if fx.exists():
            with st.expander("All the features we tested, and their weights"):
                st.dataframe(pd.read_csv(fx), hide_index=True)
    with tabs[2]:
        st.markdown("#### :material/account_tree: What every rewrite has to pass")
        st.mermaid_chart('''flowchart LR
    S["Paragraph scores 35+"] --> W["Writer rewrites it,<br/>told what pushes<br/>the score up"]
    W --> D{"Score drops<br/>by 5 or more?"}
    D -- no --> W
    D -- yes --> F{"Fluency, facts kept,<br/>no new facts"}
    F -- fail --> W
    F -- pass --> E{"Evidence check<br/>against source quotes"}
    E -- fail --> W
    E -- pass --> M{"Meaning check<br/>whole paper"}
    M -- fail --> W
    M -- pass --> K["Kept"]
    W -. "3 attempts used" .-> O["Original kept,<br/>flagged for a human edit"]''', width="stretch",
                         alt="A rewrite must lower the score by 5 and pass fluency, facts, evidence and meaning checks; otherwise the original is kept after three attempts.")
        st.caption("An independent reviewer model reads the first draft before rewriting (its notes go to the writer, "
                   "and paragraphs it says need research are not rewritten) and the final paper after. Writer, "
                   "checker and reviewer are three different models. The detector chooses and guides; only the "
                   "checks can accept a rewrite.")
        rows, reasons = d.pipeline_summary()
        st.markdown("#### :material/table_chart: What happened in the final runs")
        st.dataframe(rows, hide_index=True, column_config={
            "Score before": st.column_config.NumberColumn(format="%.0f"),
            "Score after": st.column_config.NumberColumn(format="%.0f")})
        tot = {k: sum(r[k] for r in rows) for k in ("Selected (35+)", "Rewritten", "Kept unchanged", "Held for research")}
        st.markdown(f"Across the five topics, **{tot['Rewritten']} of {tot['Selected (35+)']}** selected paragraphs were "
                    f"rewritten, {tot['Kept unchanged']} kept unchanged (flagged for a human edit) and "
                    f"{tot['Held for research']} held for research. Scores are averages over the selected paragraphs.")
        st.markdown("**Why attempts were rejected**")
        st.bar_chart(pd.DataFrame({"Reason": list(reasons), "Attempts": list(reasons.values())}),
                     x="Reason", y="Attempts", horizontal=True, color=look.MACHINE)
        st.caption("Most rejections are rewrites that changed too little. Content checks rejected the rest, and the "
                   "fluency guard stopped the writer from lowering the score by chopping sentences into fragments.")
    with tabs[3]:
        st.markdown("#### :material/bug_report: Do the checks catch planted errors?")
        seeded = d.ROOT / "sprint2_demo/evaluation/results_with_llm/summary.json"
        if seeded.exists():
            sf = json.loads(seeded.read_text(encoding="utf-8"))
            st.caption("We planted errors (changed numbers, swapped citations, made-up results and more) into real "
                       "draft paragraphs, and mixed in 30 acceptable rewrites, then ran the checks.")
            st.dataframe(d.seeded_rows(sf), hide_index=True)
            st.caption("Subtle meaning drift: rewrites that people judged to have shifted the meaning (for example "
                       "‘may’ became ‘can’). Five come from real rewrites made by an earlier version of the pipeline, "
                       "one from a hand-written rewrite.")
            st.markdown(f"Caught **{sf['fault_catch_rate']}** (including drifts judged by people); acceptable "
                        f"rewrites wrongly rejected: **{sf['false_alarms_on_clean_rewrites']}**.")
        st.markdown("#### :material/policy: What does an outside detector say?")
        gz = d.ROOT / "results/detection/human_eval_v3/gptzero_pipeline_summary.json"
        if gz.exists():
            g = json.loads(gz.read_text(encoding="utf-8"))
            st.caption("GPTZero (free web version) on the 20 short passages of our human study: 10 from real EMNLP "
                       "2025 papers and 10 from our final papers.")
            st.dataframe([{"Text": name.replace("generated", "Our final papers").replace("real", "Real EMNLP papers"),
                           "GPTZero AI %": g["gptzero_ai_mean"][name], "Our detector": g["our_detector_mean"][name],
                           "GPTZero labels": ", ".join(f"{v} {k}" for k, v in g["gptzero_labels"][name].items())}
                          for name in ("real", "generated")], hide_index=True)
            st.markdown("GPTZero still calls our rewritten passages AI, while it doubts much real academic writing too. "
                        "We treat our score as a guide to formulaic style, not proof of human authorship.")
        else:
            st.info("GPTZero results will appear here once the summary is generated.")


if not (d.BUNDLES / "index.json").exists():
    st.error("The topic files are missing. In the repo root, run `python sprint3_demo/build_demo_bundles.py`, "
             "then refresh this page.")
    st.stop()

st.navigation([st.Page(walkthrough, title="Walkthrough", icon=":material/route:", default=True),
               st.Page(own_text, title="Score and rewrite your text", icon=":material/edit_note:", url_path="your-text"),
               st.Page(detector_page, title="Detector and tests", icon=":material/troubleshoot:", url_path="detector")],
              position="top").run()
