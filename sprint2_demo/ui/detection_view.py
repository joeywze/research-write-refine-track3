"""'Detect' step: AI-likeness detector, rewriting loop, full-paper revision and human evaluation.

Reads only saved files from results/detection/ and scores text locally, so it works in the
hosted (no API key) preview as well as locally. Nothing here calls a model.
"""
from difflib import SequenceMatcher
from pathlib import Path
import json
import re
import sys

import pandas as pd
import streamlit as st

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results" / "detection"
sys.path.insert(0, str(REPO / "src" / "detection"))
from detector import PLAIN_NAMES, HEDGES, _count_terms, _WORD, score, split_sentences  # noqa: E402

CITE = re.compile(r"\[\[[^\]]+\]\]")
CLICHE = ("Furthermore, it is important to note that our robust, scalable, and efficient framework may "
          "potentially suggest a promising direction for future research. Moreover, these findings highlight "
          "the crucial role of comprehensive evaluation in a wide range of settings. Additionally, the approach "
          "could possibly enhance performance, robustness, and generalisation across diverse tasks.")


# ------------------------------------------------------------------ data (no Streamlit calls)

def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def read_csv(path):
    try:
        return pd.read_csv(path)
    except (OSError, ValueError):
        return None


def clean(text):
    t = CITE.sub("", str(text))
    t = re.sub(r"\s*;\s*\.", ".", t)
    return re.sub(r"\s+([.,;:])", r"\1", t).strip()


def presets():
    out = {"Clichéd LLM-style paragraph": CLICHE}
    v0 = read_json(REPO / "sprint2_demo" / "inputs" / "converted" / "v0.json")
    if v0:
        for p in v0["paragraphs"]:
            if p["paragraph_id"] == "P037":
                out["Our draft V0, paragraph P037 (limitations)"] = clean(p["text"])
    real = read_csv(REPO / "data" / "human_eval" / "real_passages_curated.csv")
    if real is not None:
        row = real[real.paper_id == "2025.emnlp-main.992"]
        if len(row):
            out["Real EMNLP 2025 paragraph (2025.emnlp-main.992)"] = row.text.iloc[0]
    out["Paste your own text"] = ""
    return out


def analysis(text):
    r = score(text)
    drivers = [(PLAIN_NAMES.get(n, n), c) for n, c in r["contributions"].items() if c > 0.15]
    lengths = [len(_WORD.findall(s)) for s in split_sentences(text)]
    return {"score": r["score"], "drivers": drivers, "flagged": r["flagged"], "lengths": lengths,
            "hedges": _count_terms(text.lower(), HEDGES), "n_words": r["n_words"]}


def verdict(s):
    if s < 40:
        return "Reads like a real paper", "green"
    if s < 60:
        return "Borderline", "orange"
    return "Reads like LLM output", "red"


def highlighted(text, flagged):
    """Markdown with flagged sentences highlighted."""
    def esc(s):
        return re.sub(r"([\\`*_{}\[\]<>#+!|~$])", r"\\\1", s)
    sents = split_sentences(re.sub(r"\s+", " ", text).strip())
    marked = {f["index"] for f in flagged}
    return " ".join(f":orange-background[{esc(s)}]" if i in marked else esc(s) for i, s in enumerate(sents))


def word_diff(before, after):
    def esc(s):
        return re.sub(r"([\\`*_{}\[\]()<>#+!|~$])", r"\\\1", s)
    a, b = re.findall(r"\S+|\s+", before), re.findall(r"\S+|\s+", after)
    out = []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(esc("".join(a[i1:i2])))
        if op in ("replace", "delete"):
            out.append("~~" + esc("".join(a[i1:i2])) + "~~")
        if op in ("replace", "insert"):
            out.append(":green-background[" + esc("".join(b[j1:j2])) + "]")
    return "".join(out)


def loop_data():
    log = read_csv(RESULTS / "loop_log.csv")
    if log is None or log.empty:
        return None
    mx = int(log.iteration.max())
    curve = log.groupby(["condition", "iteration"]).score.mean().unstack(0).round(1)
    first = log[log.iteration == 0].drop_duplicates(["pid", "condition"]).set_index(["pid", "condition"])
    last = log[log.iteration == mx].set_index(["pid", "condition"])
    rows = []
    for pid in log.pid.unique():
        try:
            rows.append({"pid": pid, "start": first.loc[(pid, "guided")].score,
                         "naive": last.loc[(pid, "naive")].score, "guided": last.loc[(pid, "guided")].score,
                         "original_text": first.loc[(pid, "guided")].text,
                         "naive_text": last.loc[(pid, "naive")].text, "guided_text": last.loc[(pid, "guided")].text})
        except KeyError:
            continue
    rej = log[~log.accepted.astype(bool)].groupby(["condition", "reason"]).size().reset_index(name="count")
    return {"rounds": mx, "curve": curve, "paragraphs": pd.DataFrame(rows), "rejections": rej,
            "n": log.pid.nunique()}


def label(pid):
    if pid.startswith("V0-"):
        return f"Our draft · {pid[3:]}"
    m = re.match(r"GPT-([^-]+)-(.+)-\d+$", pid)
    return f"GPT pilot · {m.group(2).replace('_', ' ')} (paper {m.group(1)})" if m else pid


def full_paper_data():
    d = RESULTS / "full_paper"
    df = read_csv(d / "paragraphs.csv")
    if df is None or df.empty:
        return None
    scored = df.dropna(subset=["v0_score"]).copy()
    scored["v3_score"] = scored.v3_score.fillna(scored.v0_score)
    order = ["abstract", "introduction", "related_work", "methodology", "experiments", "conclusion"]
    by_sec = (scored.groupby("section")[["v0_score", "v3_score"]].mean().round(1)
              .reindex([s for s in order if s in set(scored.section)]).reset_index())
    by_sec["section"] = by_sec.section.str.replace("_", " ").str.title()
    by_sec.columns = ["Section", "V0 mean score", "V3 mean score"]
    paper = d / "final_paper_v3.md"
    return {"df": df, "scored": scored, "by_section": by_sec,
            "v3_md": paper.read_text(encoding="utf-8") if paper.exists() else None,
            "revised": df[df.status == "revised"]}


def human_eval_data():
    res = read_csv(RESULTS / "human_eval" / "human_eval_results.csv")
    items = read_csv(RESULTS / "human_eval" / "PRIVATE_answer_key.csv")
    return res, items


def draft_score(draft):
    """Mean detector score over prose paragraphs (40+ words, no tables) of a Stage B Draft."""
    scores = []
    for p in draft.paragraphs:
        t = clean(p.text)
        if len(t.split()) >= 40 and not t.lstrip().startswith("|"):
            scores.append(score(t)["score"])
    return round(sum(scores) / len(scores), 1) if scores else None


def same_text(a, b):
    return [p.text for p in a.paragraphs] == [p.text for p in b.paragraphs]


# ------------------------------------------------------------------ pieces used inside app.py

def intro():
    """Objective banner shown at the top of every step."""
    with st.container(border=True):
        st.markdown("**The problem.** Papers drafted with LLMs have a recognisable style: stacked hedges, lists "
                    "of three, uniform sentence lengths, stock phrases. Reviewers notice it, and it undermines "
                    "otherwise sound research.")
        st.markdown("**Who it's for.** Researchers and students who draft papers with LLM help and want the "
                    "result to read like their own writing, without the facts, numbers or citations changing.")
        st.markdown("**What this app does.** Grounds a research idea in published EMNLP 2025 work → drafts the "
                    "paper → refines it with content checks → **measures how AI-like it reads and rewrites it "
                    "until it doesn't** (Detect).")


def stage_b_comparison(data):
    """Detector scores for Stage B's original / generic / guided drafts, plus the V3 paper. Shown in Results."""
    st.subheader("How AI-like does each version read?")
    drafts = data["drafts"]
    rows = [{"Version": "Original draft (V0)", "AI-likeness score": draft_score(drafts["v0_input"])},
            {"Version": "Generic rewrite (V1)", "AI-likeness score": draft_score(drafts["generic_final"])},
            {"Version": "Guided rewrite (V2)", "AI-likeness score": draft_score(drafts["guided_final"])}]
    fp = full_paper_data()
    if fp is not None:
        rows.append({"Version": "Detector-guided paper (V3)",
                     "AI-likeness score": round(float(fp["scored"].v3_score.mean()), 1)})
    st.dataframe(rows, hide_index=True,
                 column_config={"AI-likeness score": st.column_config.NumberColumn(format="%.1f")})
    st.caption("Our detector's mean score over prose paragraphs: 0 = reads like a real EMNLP paper, 100 = reads "
               "like LLM output. Real paper text has a median of about 28.")
    notes = []
    if same_text(drafts["generic_final"], drafts["v0_input"]):
        notes.append("The generic rewrite (a plain \"improve the writing\" instruction) made no changes in this run, "
                     "the plateau the assignment brief predicts for that kind of prompt.")
    notes.append("The review points above can fall to zero while the AI-likeness score barely moves: Stage B fixes "
                 "specific wording issues, but not the overall style.")
    if fp is not None:
        notes.append("The detector-guided loop in **Detect** rewrites style directly and brings the paper into the "
                     "real-paper range.")
    for n in notes:
        st.caption(n)
    if fp is not None:
        st.info("The final paper is **V3** (detector-guided). Read and download it in **Detect → Final paper (V3)**.")


def justification():
    """'Why this detector' panel for requirement 1 of Half 2."""
    with st.container(border=True):
        st.markdown("#### Why this detector")
        st.markdown(
            "- **Stylometric features with learned weights,** rather than a black-box classifier or an LLM judge. "
            "Every point of the score traces back to a specific sentence and reason (a hedge, a list of three, "
            "uniform sentence lengths), so the rewriting loop can be told *what* to fix. It is also free and "
            "instant, so it can run inside the loop and in this hosted app.\n"
            "- **Calibrated on real papers:** each feature is measured against 1,808 real EMNLP 2025 abstracts, and "
            "a logistic regression learns how much each one separates them from 386 GPT paragraphs.\n"
            "- **Weights can only point the expected way** (more hedging can only mean more AI-like). Without this, "
            "the model learned that real abstracts use words like *robust* and *significant* more than our GPT "
            "text did, and the loop would have been rewarded for adding clichés.\n"
            "- **Not TF-IDF:** it scored higher (AUC 0.99) but by learning topic words, not style, and it gives the "
            "rewriter nothing actionable.\n"
            "- **Not numbers or citations:** our generator was told not to invent them, so those features measure "
            "the prompt; optimising them would push the rewriter to fabricate.")
        st.markdown(
            "**What survived from the brief's suggested features:** hedge density and sentence length (how much "
            "it varies, and the share of long sentences) carry the most weight, along with stock phrases and "
            "lists of three. N-gram repetition and "
            "promotional adjectives (our stand-in for adjective ratio) got zero weight: they did not separate "
            "real from generated text in this data.")
        st.markdown(
            "**Known limits:** the training data is mostly abstracts (checked against held-out body text, "
            "AUC 0.83); about 1 in 6 real passages scores above 50; and a rewriter optimising this score can "
            "game it, which is why the loop has a fluency guard and why the human evaluation is the final test.")


# ------------------------------------------------------------------ project overview (shown on every step)

# Edit owners / status here.
FEATURES = [
    ("Literature corpus: 1,809 EMNLP 2025 papers, topic clustering, Cluster 7 gap analysis", "Joey Wong", "Done"),
    ("Claim-to-evidence ledger and fact checker", "Tabitha Tay, Joey Wong", "Done (pilot)"),
    ("Research package and draft V0", "Joey Wong", "Done · team approval pending"),
    ("Stage B: rule + LLM critique, guided rewrite, content-preservation checks", "Tan Guan Hong", "Done"),
    ("Demo app (this site)", "Tan Guan Hong, Wan Yun", "Done"),
    ("AI-likeness detector (stylometric, calibrated on real EMNLP text)", "Wan Yun", "Done"),
    ("Detector-guided rewriting loop with fluency guard; full-paper revision V3", "Wan Yun", "Done"),
    ("Human evaluation: real vs generated", "Wan Yun", "In progress"),
    ("Semantic preservation check on V3; more drafts and raters", "Team", "Planned"),
]


def about():
    with st.expander("About this project: pipeline, team and status"):
        st.mermaid_chart('''flowchart LR
    A["Research<br/>1,809 EMNLP papers → gap"] --> B["Draft<br/>V0, six sections"]
    B --> C["Refine<br/>critic + checked rewrite (V2)"]
    C --> D["Detect<br/>AI-likeness score"]
    D -->|"guided feedback"| E["Rewrite loop<br/>final paper V3"]
    E --> D
    D --> F["Human evaluation<br/>real vs generated"]''', width="stretch",
                         alt="Pipeline: research, draft, refine, detect, detector-guided rewrite loop producing V3, human evaluation.")
        st.markdown("| Feature | Owner | Status |\n|---|---|---|\n" +
                    "\n".join(f"| {f} | {o} | {s} |" for f, o, s in FEATURES))
        st.markdown("**How we show it works:** detector AUC on unseen real papers; detector score across rewrite "
                    "rounds (naive prompt vs detector-guided); content checks that reject changed numbers, citations "
                    "and terms; and people guessing real vs generated, where 50% means they cannot tell.")


# ------------------------------------------------------------------ page

def show():
    st.header("How AI-like is the writing?")
    st.caption("Our stylometric detector scores writing style from 0 (reads like a real EMNLP paper) to 100 "
               "(reads like LLM output). It runs here without any model calls.")
    tabs = st.tabs(["Score any text", "Is the detector valid?", "Rewriting loop", "Final paper (V3)",
                    "Human evaluation"])

    # ---------------- 1. score any text
    with tabs[0]:
        options = presets()
        choice = st.selectbox("Example text", list(options), key="det_preset")
        text = st.text_area("Text to score (one paragraph works best)", value=options[choice], height=180,
                            key="det_text_" + str(list(options).index(choice)))
        if text.strip() and len(text.split()) >= 15:
            a = analysis(text)
            word, color = verdict(a["score"])
            cols = st.columns(3)
            cols[0].metric("AI-likeness score", f"{a['score']:.0f} / 100")
            cols[1].metric("Hedge words", a["hedges"])
            cols[2].metric("Sentence lengths (words)", ", ".join(map(str, a["lengths"][:8])) or "–")
            st.badge(word, color=color)
            st.caption("For scale: real EMNLP paper text has a median of about 28; raw GPT paragraphs about 61.")
            if a["drivers"]:
                st.markdown("**What pushes the score up:** " + "; ".join(n for n, _ in a["drivers"]))
            st.markdown("**Flagged sentences** (highlighted):")
            st.markdown(highlighted(text, a["flagged"]))
            for f in a["flagged"][:8]:
                st.caption(f"Sentence {f['index'] + 1}: " + "; ".join(f["reasons"]))
        else:
            st.info("Enter at least a sentence or two (15+ words) to score.")

    # ---------------- 2. validation
    with tabs[1]:
        val = read_json(RESULTS / "detector_validation.json") or {}
        ho = read_json(RESULTS / "heldout_fulltext.json") or {}
        justification()
        cols = st.columns(3)
        if ho:
            cols[0].metric("AUC on unseen real paper text", f"{ho['auc_body_text_heldout']:.2f}",
                           help="344 passages from 18 EMNLP papers the detector never saw. 0.5 = coin flip, 1.0 = perfect.")
        if val:
            cols[1].metric("AUC, cross-validated", f"{val['auc_stylometric_all']:.2f}")
            cols[2].metric("TF-IDF baseline AUC (not used)", f"{val['auc_tfidf_all']:.2f}",
                           help="Higher, but it learns topic words rather than style and gives the rewriter nothing to act on.")
        img = RESULTS / "detector_validation.png"
        if img.exists():
            st.image(str(img), caption="Score distributions: real paper text vs GPT text vs our draft.")
        st.markdown("Given one real and one generated paragraph, the detector ranks the generated one as more "
                    "AI-like about 83% of the time. It is not perfect: about 1 in 6 real passages scores above 50.")
        fx = read_csv(RESULTS / "feature_effects.csv")
        if fx is not None:
            with st.expander("Which features matter (and which folk-wisdom ones don't)"):
                st.caption("Words like 'robust', 'crucial' and 'significant' appear MORE in real EMNLP abstracts than "
                           "in our GPT text, so they got zero weight.")
                st.dataframe(fx, hide_index=True)

    # ---------------- 3. loop
    with tabs[2]:
        ld = loop_data()
        if ld is None:
            st.info("No rewriting-loop results yet. Run `python src/detection/rewrite_loop.py --n 10 --iters 4`.")
        else:
            st.markdown(f"**{ld['n']} paragraphs × {ld['rounds']} rounds**, two ways from the same start: a naive "
                        "*\"make it sound human\"* prompt, and detector-guided feedback naming the exact problems.")
            c = ld["curve"]
            cols = st.columns(2)
            cols[0].metric("Naive prompt", f"{c['naive'].iloc[-1]:.0f}",
                           f"{c['naive'].iloc[-1] - c['naive'].iloc[0]:+.0f} from {c['naive'].iloc[0]:.0f}",
                           delta_color="inverse")
            cols[1].metric("Detector-guided", f"{c['guided'].iloc[-1]:.0f}",
                           f"{c['guided'].iloc[-1] - c['guided'].iloc[0]:+.0f} from {c['guided'].iloc[0]:.0f}",
                           delta_color="inverse")
            for name, cap in (("loop_curve.png", "With fluency guard"),
                              ("loop_curve_v1_unguarded.png", "First run, no fluency guard: the model gamed the "
                               "detector by chopping sentences into fragments (Goodhart's law)")):
                if (RESULTS / name).exists():
                    st.image(str(RESULTS / name), caption=cap)
            if len(ld["rejections"]):
                with st.expander("Rewrites rejected by the safety checks"):
                    st.dataframe(ld["rejections"], hide_index=True)
            st.subheader("Compare one paragraph")
            p = ld["paragraphs"].sort_values("start", ascending=False)
            pick = st.selectbox("Paragraph", list(p.pid), format_func=label, key="det_loop_pid")
            row = p[p.pid == pick].iloc[0]
            cols = st.columns(3, gap="medium")
            for col, title, key, s in ((cols[0], "Original", "original_text", row.start),
                                       (cols[1], "Naive prompt", "naive_text", row.naive),
                                       (cols[2], "Detector-guided", "guided_text", row.guided)):
                with col:
                    st.caption(f"{title} · score {s:.0f}")
                    st.markdown(clean(row[key]))
            with st.expander("Highlight what the guided rewrite changed"):
                st.markdown(word_diff(clean(row.original_text), clean(row.guided_text)))

    # ---------------- 4. full paper
    with tabs[3]:
        fp = full_paper_data()
        if fp is None:
            st.info("The full-paper revision has not been run yet. Run `python src/detection/revise_full_paper.py`.")
        else:
            s = fp["scored"]
            cols = st.columns(3)
            cols[0].metric("Mean score, V0", f"{s.v0_score.mean():.0f}")
            cols[1].metric("Mean score, V3", f"{s.v3_score.mean():.0f}",
                           f"{s.v3_score.mean() - s.v0_score.mean():+.0f}", delta_color="inverse")
            cols[2].metric("Paragraphs revised", f"{len(fp['revised'])} of {len(fp['df'])}")
            st.dataframe(fp["by_section"], hide_index=True)
            st.caption("Tables and the research-question list were never sent to the model. Every kept rewrite "
                       "preserved citations, numbers and protected terms and passed the fluency guard.")
            if fp["v3_md"]:
                st.download_button("Download final paper (V3)", fp["v3_md"].encode("utf-8"),
                                   file_name="final_paper_v3.md", mime="text/markdown", type="primary",
                                   icon=":material/download:", key="det_dl_v3")
                with st.expander("Read the final paper (V3)"):
                    st.markdown(fp["v3_md"])
            if len(fp["revised"]):
                st.subheader("What changed")
                rv = fp["revised"]
                pick = st.selectbox("Revised paragraph", list(rv.pid), key="det_fp_pid",
                                    format_func=lambda x: f"{x} · {rv[rv.pid == x].section.iloc[0].replace('_', ' ')}")
                r = rv[rv.pid == pick].iloc[0]
                cols = st.columns(2, gap="large")
                with cols[0]:
                    st.caption(f"V0 · score {r.v0_score:.0f}")
                    st.markdown(clean(r.v0_text))
                with cols[1]:
                    st.caption(f"V3 · score {r.v3_score:.0f}")
                    st.markdown(clean(r.v3_text))
                with st.expander("Highlight changed words"):
                    st.markdown(word_diff(clean(r.v0_text), clean(r.v3_text)))
                if _count_terms(clean(r.v3_text).lower(), HEDGES) < _count_terms(clean(r.v0_text).lower(), HEDGES):
                    st.warning("This rewrite removed hedge words. Check that it does not overstate the claim.")

    # ---------------- 5. human evaluation
    with tabs[4]:
        res, items = human_eval_data()
        st.markdown("People see 12 paragraphs on the same topic: **6 from real EMNLP 2025 papers**, **3 from our "
                    "draft V0** and **3 rewritten by the detector-guided loop**, and say *Real paper* or "
                    "*Generated*. **50% accuracy means they cannot tell** (the target).")
        if res is None:
            st.info("Responses are being collected. Results will appear here once scored with "
                    "`python src/detection/human_eval.py score responses.csv`.")
            if items is not None and {"condition", "item_id"} <= set(items.columns):
                agg = {"items": ("item_id", "count")}
                if "detector_score" in items.columns:
                    agg["mean_detector_score"] = ("detector_score", "mean")
                summary = items.groupby("condition").agg(**agg).round(1)
                st.caption("Test set, with the detector's own scores:")
                st.dataframe(summary.reset_index(), hide_index=True)
        else:
            overall = res.iloc[0]
            st.metric("Human detection accuracy", f"{overall.accuracy:.0%}",
                      help=f"95% interval {overall.ci95_low:.0%}-{overall.ci95_high:.0%}, {int(overall.n)} judgements")
            st.dataframe(res, hide_index=True)
            per_item = read_csv(RESULTS / "human_eval" / "human_eval_per_item.csv")
            if per_item is not None and "detector_score" in per_item:
                rho = per_item[["detector_score", "share_said_generated"]].corr(method="spearman").iloc[0, 1]
                st.caption(f"Detector vs humans: Spearman correlation {rho:.2f} between an item's detector score "
                           "and the share of raters who called it generated.")
