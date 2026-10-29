"""Plain-English guides for every step, plus step 5 "Make it read human" (Track 3, Half 2).

Reads only saved files from results/detection/ and scores text locally, so it works in the hosted
(no API key) preview as well as locally. Nothing here calls a model.
"""
from difflib import SequenceMatcher
from pathlib import Path
import json
import re
import sys

import pandas as pd
import streamlit as st

import look

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results" / "detection"
sys.path.insert(0, str(REPO / "src" / "detection"))
from detector import PLAIN_NAMES, HEDGES, _count_terms, _WORD, score, split_sentences  # noqa: E402

CITE = re.compile(r"\[\[[^\]]+\]\]")

# ------------------------------------------------------------------ names used everywhere on the site
FIRST = "First draft"
PLAIN = "Plain rewrite"
REVIEWED = "Reviewer-checked edit"
FINAL = "Final paper"
VERSION_INFO = [
    (FIRST, "Written by an LLM from the research package. Nothing changed yet."),
    (PLAIN, "The LLM was simply told to \"improve the writing\". The usual shortcut."),
    (REVIEWED, "A reviewer (rules + an LLM critic) flagged specific wording problems; the LLM fixed them, and "
               "content checks made sure no facts, numbers or citations changed."),
    (FINAL, "Our AI-likeness detector told the LLM exactly what sounds machine-written, paragraph by paragraph, "
            "until it read like a real paper. Same content checks."),
]
STEPS = {"Research": "1 · Research idea", "Draft": "2 · First draft", "Refine": "3 · Reviewer-checked edit",
         "Results": "4 · Compare versions", "Detect": "5 · Make it read human"}
STEP_ICONS = {"Research": ":material/travel_explore:", "Draft": ":material/article:",
              "Refine": ":material/rate_review:", "Results": ":material/compare_arrows:",
              "Detect": ":material/auto_fix_high:"}
VERSION_COLOURS = [look.MACHINE, look.MACHINE, look.MID, look.HUMAN]
NAIVE_LABEL = "\"Sound more human\" prompt"
GUIDED_LABEL = "Detector-guided"

CLICHE = ("Furthermore, it is important to note that our robust, scalable, and efficient framework may "
          "potentially suggest a promising direction for future research. Moreover, these findings highlight "
          "the crucial role of comprehensive evaluation in a wide range of settings. Additionally, the approach "
          "could possibly enhance performance, robustness, and generalisation across diverse tasks.")

# Edit owners / status here.
FEATURES = [
    ("Literature corpus: 1,809 EMNLP 2025 papers, topic clustering, gap analysis", "Joey Wong", "Done"),
    ("Claim-to-evidence ledger and fact checker", "Tabitha Tay, Joey Wong", "Done (pilot)"),
    ("Research package and first draft", "Joey Wong", "Done · team approval pending"),
    ("Reviewer-checked edit: rule + LLM critique, rewrite, content checks", "Tan Guan Hong", "Done"),
    ("Demo site", "Tan Guan Hong, Wan Yun", "Done"),
    ("AI-likeness detector, calibrated on real EMNLP text", "Wan Yun", "Done"),
    ("Detector-guided rewriting loop and final paper", "Wan Yun", "Done"),
    ("Human test: real vs generated paragraphs", "Wan Yun", "Planned"),
    ("Meaning check on the final paper; more drafts and readers", "Team", "Planned"),
]


# ------------------------------------------------------------------ data helpers (no Streamlit calls)

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
    out = {"A clichéd, LLM-style paragraph": CLICHE}
    v0 = read_json(REPO / "sprint2_demo" / "inputs" / "converted" / "v0.json")
    if v0:
        for p in v0["paragraphs"]:
            if p["paragraph_id"] == "P037":
                out["A paragraph from our first draft (limitations)"] = clean(p["text"])
    fp = read_csv(RESULTS / "full_paper" / "paragraphs.csv")
    if fp is not None and "P037" in set(fp.pid):
        r = fp[fp.pid == "P037"].iloc[0]
        if r.status == "revised":
            out["The same paragraph in our final paper"] = clean(r.v3_text)
    real = read_csv(REPO / "data" / "human_eval" / "real_passages_curated.csv")
    if real is not None:
        row = real[real.paper_id == "2025.emnlp-main.992"]
        if len(row):
            out["A paragraph from a real EMNLP 2025 paper"] = row.text.iloc[0]
    out["Paste your own text"] = ""
    return out


def analysis(text):
    r = score(text)
    drivers = [PLAIN_NAMES.get(n, n) for n, c in r["contributions"].items() if c > 0.15]
    lengths = [len(_WORD.findall(s)) for s in split_sentences(text)]
    return {"score": r["score"], "drivers": drivers, "flagged": r["flagged"], "lengths": lengths,
            "hedges": _count_terms(text.lower(), HEDGES)}


def verdict(s):
    if s < 40:
        return "Reads like a real paper", "green"
    if s < 60:
        return "Borderline", "orange"
    return "Reads like LLM output", "red"


def _esc(s):
    return re.sub(r"([\\`*_{}\[\]<>#+!|~$])", r"\\\1", s)


def highlighted(text, flagged):
    sents = split_sentences(re.sub(r"\s+", " ", text).strip())
    marked = {f["index"] for f in flagged}
    return " ".join(f":orange-background[{_esc(s)}]" if i in marked else _esc(s) for i, s in enumerate(sents))


def word_diff(before, after):
    a, b = re.findall(r"\S+|\s+", before), re.findall(r"\S+|\s+", after)
    out = []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(_esc("".join(a[i1:i2])))
        if op in ("replace", "delete"):
            out.append("~~" + _esc("".join(a[i1:i2])) + "~~")
        if op in ("replace", "insert"):
            out.append(":green-background[" + _esc("".join(b[j1:j2])) + "]")
    return "".join(out)


def colours(df):
    return [look.HUMAN if c == GUIDED_LABEL else look.MACHINE if c == NAIVE_LABEL else look.INK for c in df.columns]


def para_label(pid):
    if pid.startswith("V0-"):
        return f"Our first draft · paragraph {pid[3:]}"
    m = re.match(r"GPT-([^-]+)-(.+)-\d+$", pid)
    return f"GPT-written {m.group(2).replace('_', ' ')} (EMNLP paper {m.group(1).lstrip('.')})" if m else pid


def loop_data(name="loop_log.csv"):
    log = read_csv(RESULTS / name)
    if log is None or log.empty:
        return None
    log["accepted"] = log.accepted.astype(str).str.lower().isin(["true", "1"])
    mx = int(log.iteration.max())
    curve = log.groupby(["iteration", "condition"]).score.mean().unstack()
    curve = curve.rename(columns={"naive": NAIVE_LABEL, "guided": GUIDED_LABEL})
    curve.index.name = "Round"
    curve.columns.name = None
    rounds = []
    for it in range(mx + 1):
        row = {"Round": "Start" if it == 0 else it,
               NAIVE_LABEL: round(curve.loc[it, NAIVE_LABEL], 1),
               GUIDED_LABEL: round(curve.loc[it, GUIDED_LABEL], 1)}
        if it:
            g = log[(log.iteration == it) & (log.condition == "guided")]
            row["Guided rewrites kept"] = f"{int(g.accepted.sum())} of {len(g)}"
        else:
            row["Guided rewrites kept"] = ""
        rounds.append(row)
    rej = (log[(~log.accepted) & (log.iteration > 0)].groupby(["condition", "reason"]).size()
           .reset_index(name="Rewrites rejected"))
    rej["condition"] = rej.condition.map({"naive": NAIVE_LABEL, "guided": GUIDED_LABEL})
    rej = rej.rename(columns={"condition": "Method", "reason": "Why it was rejected"})
    return {"log": log, "rounds": mx, "curve": curve.round(1), "table": pd.DataFrame(rounds),
            "rejections": rej, "n": log.pid.nunique()}


def paragraph_trajectory(log, pid):
    g = log[log.pid == pid].sort_values("iteration")
    chart = g.pivot_table(index="iteration", columns="condition", values="score").rename(
        columns={"naive": NAIVE_LABEL, "guided": GUIDED_LABEL})
    chart.index.name = "Round"
    chart.columns.name = None
    steps = []
    for r in g[(g.condition == "guided") & (g.iteration > 0)].itertuples():
        cand = getattr(r, "candidate_score", None)
        steps.append({"Round": r.iteration,
                      "Detector-guided outcome": "Kept" if r.accepted else f"Rejected: {r.reason}",
                      "Rewrite scored": "" if cand is None or pd.isna(cand) else round(cand, 1),
                      "Score after round": round(r.score, 1)})
    return chart, pd.DataFrame(steps)


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
    by_sec.columns = ["Section", f"{FIRST} score", f"{FINAL} score"]
    paper = d / "final_paper_v3.md"
    first = d / "v0_paper.md"
    rounds = None
    prog = read_json(d / "progress.json")
    if prog:
        mx = max((len(r["attempts"]) for r in prog.values()), default=0)
        cur = {k: r["v0_score"] for k, r in prog.items() if r.get("v0_score") is not None}
        series = [sum(cur.values()) / len(cur)] if cur else []
        for i in range(mx):
            for k, r in prog.items():
                if k in cur and len(r["attempts"]) > i and r["attempts"][i]["accepted"]:
                    cur[k] = r["attempts"][i]["candidate_score"]
            series.append(sum(cur.values()) / len(cur))
        if series:
            rounds = pd.DataFrame({"Whole paper, mean score": [round(x, 1) for x in series]})
            rounds.index.name = "Round"
    return {"df": df, "scored": scored, "by_section": by_sec, "rounds": rounds,
            "final_md": paper.read_text(encoding="utf-8") if paper.exists() else None,
            "first_md": first.read_text(encoding="utf-8") if first.exists() else None,
            "revised": df[df.status == "revised"]}


def human_eval_data():
    d = RESULTS / "human_eval"
    res = read_csv(d / "human_eval_results.csv")
    if res is None or res.empty:
        return None
    return {"results": res, "per_item": read_csv(d / "human_eval_per_item.csv"),
            "reasons": read_csv(d / "human_eval_reasons.csv")}


def draft_score(draft):
    scores = []
    for p in draft.paragraphs:
        t = clean(p.text)
        if len(t.split()) >= 40 and not t.lstrip().startswith("|"):
            scores.append(score(t)["score"])
    return round(sum(scores) / len(scores), 1) if scores else None


def same_text(a, b):
    return [p.text for p in a.paragraphs] == [p.text for p in b.paragraphs]


# ------------------------------------------------------------------ site-wide pieces

def step_label(stage):
    return f"{STEP_ICONS.get(stage, '')} {STEPS.get(stage, stage)}".strip()


def journey_points():
    """(label, score, kind) for the header meter: our paper's journey against real and GPT text."""
    pts = []
    fp = full_paper_data()
    if fp is not None:
        s = fp["scored"]
        pts += [(FIRST, float(s.v0_score.mean()), "up"), (FINAL, float(s.v3_score.mean()), "up")]
    real = read_csv(RESULTS / "heldout_fulltext_passages.csv")
    pts.append(("Real EMNLP papers", float(real.score.median()) if real is not None else 28.0, "down"))
    pts.append(("Raw GPT text", 61.0, "down"))
    return pts


def header():
    look.style()
    look.hero("Research Write Refine",
              "From a research gap in published work to a paper that reads like a person wrote it, "
              "without changing its facts.", "DSS5105 · Track 3 · Group 17")


def welcome():
    """Objective + how the site works. Expanded on the first step, collapsed elsewhere."""
    first = st.session_state.get("stage", "Research") == "Research"
    with st.expander("Start here: what this site does and how to use it", expanded=first, icon=":material/explore:"):
        st.markdown("**The problem.** Research papers drafted with an LLM have a recognisable style: stacked hedges "
                    "(*may potentially suggest*), lists of three, every sentence the same length, stock phrases. "
                    "Readers notice it.")
        st.markdown("**Who it's for.** Researchers and students who draft with an LLM and want the paper grounded "
                    "in real literature and readable as human writing, without its facts changing.")
        look.meter(journey_points(), "Where our paper started and finished on the detector's scale")
        st.markdown("**How to use the site.** Go through the five steps in the bar below, left to right:")
        st.mermaid_chart('''flowchart LR
    A["1 · Research idea<br/>gap found in 1,809<br/>EMNLP 2025 papers"] --> B["2 · First draft<br/>six sections,<br/>written by an LLM"]
    B --> C["3 · Reviewer-checked edit<br/>flagged wording fixed,<br/>facts protected"]
    C --> D["4 · Compare versions<br/>how much did<br/>each one help?"]
    D --> E["5 · Make it read human<br/>detector-guided<br/>final paper"]''', width="stretch",
                         alt="Five steps: research idea, first draft, reviewer-checked edit, compare versions, make it read human.")
        st.markdown("**The four versions of the paper you will see:**")
        look.versions([(i + 1, n, d, c) for i, ((n, d), c) in enumerate(zip(VERSION_INFO, VERSION_COLOURS))])
        st.caption("Everything shown is a saved run of the real system. Running new rewrites needs an API key and "
                   "is switched off in this online preview.")


def about():
    with st.expander("Team, status and how we show it works", icon=":material/groups:"):
        st.markdown("| Part | Owner | Status |\n|---|---|---|\n" +
                    "\n".join(f"| {f} | {o} | {s} |" for f, o, s in FEATURES))
        st.markdown("**How we show it works:** the detector is tested on real papers it never saw; the score is "
                    "tracked across rewrite rounds against a plain \"sound more human\" prompt; content checks "
                    "reject any rewrite that changes a number, citation or key term.")


GUIDES = {
    "Research": ["See the research gap this paper addresses, found by reviewing EMNLP 2025 papers.",
                 "Open **Research questions and proposed contribution** for the study design.",
                 "Pick a finding under **Check the supporting evidence** to read the exact source passage, then "
                 "open the paper at that page."],
    "Draft": [f"This is the **{FIRST}**: the full six-section paper an LLM wrote from the research package.",
              "Read it all, or pick one section. Notice the style: it is accurate but reads like an LLM wrote it.",
              "Download it if you want to compare it with the later versions."],
    "Refine": ["A reviewer (simple rules plus an LLM critic) flagged specific wording problems in the first draft.",
               "Open each flagged point to see the problem and the suggested fix, then the original and revised "
               "wording side by side.",
               "Changes were kept only if no number, citation or protected term changed."],
    "Results": ["The tables compare the versions: first how many wording problems the reviewer still flags, then "
                "how AI-like each version reads.",
                "Try **Test a change to a study detail** to watch the content check reject a changed number.",
                "Then continue to step 5 to see how we made the paper read human."],
}


GUIDE_ICONS = {"Research": "🔎", "Draft": "📄", "Refine": "🖊️", "Results": "⚖️", "Detect": "✨"}


def guide(stage):
    tips = GUIDES.get(stage)
    if tips:
        look.guide("How to use this page", tips, GUIDE_ICONS.get(stage, "🧭"))


def stage_b_comparison(data):
    """'How AI-like does each version read?' table on Compare versions."""
    st.subheader(":material/speed: How AI-like does each version read?")
    drafts = data["drafts"]
    rows = [{"Version": FIRST, "AI-likeness score": draft_score(drafts["v0_input"])},
            {"Version": PLAIN, "AI-likeness score": draft_score(drafts["generic_final"])},
            {"Version": REVIEWED, "AI-likeness score": draft_score(drafts["guided_final"])}]
    fp = full_paper_data()
    if fp is not None:
        rows.append({"Version": FINAL + " (detector-guided)",
                     "AI-likeness score": round(float(fp["scored"].v3_score.mean()), 1)})
    look.meter([(r["Version"].replace(" (detector-guided)", ""), r["AI-likeness score"], "up")
                for r in rows if r["Version"] in (FIRST, FINAL + " (detector-guided)")] +
               [(f"{PLAIN} / {REVIEWED}", rows[2]["AI-likeness score"], "down")],
               "The four versions on the detector's scale")
    st.dataframe(rows, hide_index=True,
                 column_config={"AI-likeness score": st.column_config.NumberColumn(format="%.1f")})
    if same_text(drafts["generic_final"], drafts["v0_input"]):
        st.caption(f"The **{PLAIN}** made no changes at all in this run: just telling an LLM to \"improve the "
                   "writing\" does not change the style.")
    st.caption(f"The **{REVIEWED}** fixed every flagged point, yet its AI-likeness score barely moved: it fixed "
               "individual wording, not the overall style.")
    if fp is not None:
        st.info(f"The **{FINAL}** brings the score into the real-paper range. See how in "
                f"**{STEPS['Detect']}**, where you can also read and download it.", icon=":material/arrow_forward:")


def score_scale():
    return (":green-badge[0-40 · reads like a real paper] :orange-badge[40-60 · borderline] "
            ":red-badge[60-100 · reads like LLM output]  \nReal EMNLP paper text scores about **28** on average; "
            "raw GPT paragraphs about **61**.")


# ------------------------------------------------------------------ step 5

def justification():
    st.markdown("#### :material/lightbulb: Why we built it this way")
    st.markdown(
        "- **Style features with learned weights, not a black-box classifier or an LLM judge.** Every point of "
        "the score traces back to a specific sentence and reason (a hedge, a list of three, uniform sentence "
        "lengths), so the rewriter can be told *what* to fix. It is also free and instant, so it can run inside "
        "the loop and on this site.\n"
        "- **Calibrated on real papers:** each feature is measured against 1,808 real EMNLP 2025 abstracts, and a "
        "logistic regression learns how much each one separates them from 386 GPT-written paragraphs.\n"
        "- **Weights can only point the expected way** (more hedging can only mean more AI-like). Without this, "
        "the model learned that real abstracts use *robust* and *significant* more than our GPT text did, and the "
        "rewriter would have been rewarded for adding clichés.\n"
        "- **Not TF-IDF word counts:** that scored higher (AUC 0.99) but by learning topic words, not style, and "
        "it gives the rewriter nothing to act on.\n"
        "- **Not numbers or citations:** our generator was told not to invent them, so those features measure the "
        "prompt; optimising them would push the rewriter to make things up.")
    st.markdown(
        "**Which of the brief's suggested features survived:** hedge density and sentence-length variation carry "
        "the most weight, along with stock phrases and lists of three. N-gram repetition and promotional "
        "adjectives (our stand-in for adjective ratio) were tested and got zero weight: they did not separate "
        "real from generated text in this data.")
    st.markdown(
        "**Known limits:** the training data is mostly abstracts (so we tested it on held-out body text); about "
        "1 in 6 real passages scores above 50; and a rewriter that optimises this score can game it, which is why "
        "the loop has a fluency guard.")


def show():
    st.header(":material/auto_fix_high: Make it read human")
    st.caption("Track 3, Half 2: measure how AI-sounding the paper is, then rewrite it until it isn't.")
    look.guide("How to use this step", [
        "**Try it**: paste any paragraph and see its score and the sentences that sound machine-written.",
        "**1 · The detector**: what it measures, why we built it this way, and how well it works.",
        "**2 · Rewriting loop**: watch the score fall round by round, against a plain prompt that plateaus.",
        "**3 · Before and after**: the same content, first draft and final paper side by side."], "✨")
    with st.expander("See the tabs as a diagram", icon=":material/account_tree:"):
        st.mermaid_chart('''flowchart LR
    T["Try it<br/>score any text"] --> D["1 · The detector<br/>what it measures,<br/>is it any good?"]
    D --> L["2 · Rewriting loop<br/>score falls round<br/>by round"]
    L --> B["3 · Before and after<br/>same content,<br/>side by side"]''', width="stretch",
                         alt="Tabs in order: try it, the detector, the rewriting loop, before and after.")
        st.markdown(score_scale())

    he = human_eval_data()
    names = [":material/edit_note: Try it", ":material/troubleshoot: 1 · The detector",
             ":material/autorenew: 2 · Rewriting loop", ":material/compare: 3 · Before and after"]
    if he is not None:
        names.append(":material/groups: 4 · Human test")
    tabs = st.tabs(names)

    # ---------------- Try it
    with tabs[0]:
        st.caption("Pick an example or paste your own paragraph. The detector scores it instantly and highlights "
                   "the sentences that sound machine-written.")
        options = presets()
        choice = st.selectbox("Example text", list(options), key="det_preset")
        text = st.text_area("Text to score (one paragraph works best)", value=options[choice], height=170,
                            key="det_text_" + str(list(options).index(choice)))
        if text.strip() and len(text.split()) >= 15:
            a = analysis(text)
            word, color = verdict(a["score"])
            look.meter([("This text", a["score"], "up"), ("Real EMNLP papers", 28, "down"),
                        ("Raw GPT text", 61, "down")], f"Score {a['score']:.0f} / 100: {word.lower()}")
            cols = st.columns(2)
            cols[0].metric("Hedge words", a["hedges"], help="may, might, could, potentially, suggests ...")
            cols[1].metric("Sentence lengths (words)", ", ".join(map(str, a["lengths"][:8])) or "–",
                           help="Real writing mixes short and long sentences.")
            if a["drivers"]:
                st.markdown("**What pushes the score up:** " + "; ".join(a["drivers"]))
            st.markdown("**Flagged sentences** (highlighted):")
            st.markdown(highlighted(text, a["flagged"]))
            for f in a["flagged"][:8]:
                st.caption(f"Sentence {f['index'] + 1}: " + "; ".join(f["reasons"]))
        else:
            st.info("Enter at least a sentence or two (15+ words) to score.")

    # ---------------- 1 detector
    with tabs[1]:
        st.caption("Criterion 1: measure how AI-sounding a draft is, and justify the choice. Read what it "
                   "measures, why we built it this way, and how well it works on papers it never saw.")
        st.markdown("#### :material/straighten: What it measures")
        st.markdown("| Signal | What LLM text tends to do |\n|---|---|\n"
                    "| Hedge density | stacks *may, could, potentially, suggests* everywhere |\n"
                    "| Sentence-length variation | keeps every sentence about the same length |\n"
                    "| Long sentences | avoids the long, dense sentences real papers use |\n"
                    "| Stock phrases | *it is important to note, plays a crucial role, these findings highlight* |\n"
                    "| Lists of three | \"robust, scalable, and efficient\" in sentence after sentence |")
        justification()
        st.markdown("#### :material/verified: Does it work?")
        val = read_json(RESULTS / "detector_validation.json") or {}
        ho = read_json(RESULTS / "heldout_fulltext.json") or {}
        cols = st.columns(3)
        if ho:
            cols[0].metric("Accuracy on unseen papers (AUC)", f"{ho['auc_body_text_heldout']:.2f}",
                           help="344 passages from 18 real EMNLP papers it never saw. 0.5 = coin flip, 1.0 = perfect.")
        if val:
            cols[1].metric("Cross-validated AUC", f"{val['auc_stylometric_all']:.2f}")
            cols[2].metric("Word-count baseline (not used)", f"{val['auc_tfidf_all']:.2f}",
                           help="Higher, but it learns topic words rather than style.")
        st.markdown("In plain terms: given one real and one generated paragraph, the detector picks the generated "
                    "one as more AI-like about **83% of the time**.")
        img = RESULTS / "detector_validation.png"
        if img.exists():
            st.image(str(img), caption="Scores for real paper text, GPT text and our first draft.")
        fx = read_csv(RESULTS / "feature_effects.csv")
        if fx is not None:
            with st.expander("All 18 features we tested, and their weights"):
                st.caption("Words like *robust*, *crucial* and *significant* appear MORE in real EMNLP abstracts "
                           "than in our GPT text, so the popular 'AI word list' idea got zero weight.")
                st.dataframe(fx, hide_index=True)

    # ---------------- 2 loop
    with tabs[2]:
        st.caption("Criterion 2: the generator writes, the detector scores, the system revises, and the score "
                   "improves round by round.")
        st.mermaid_chart('''flowchart LR
    P["LLM-written<br/>paragraph"] --> S["Detector scores it<br/>and names the problems"]
    S --> R["LLM rewrites,<br/>fixing those problems"]
    R --> C{"Checks: same numbers,<br/>citations, terms?<br/>fluent? score lower?"}
    C -->|"yes: keep"| S
    C -->|"no: reject,<br/>keep previous"| S''', width="stretch",
                         alt="Loop: paragraph, detector scores and names problems, LLM rewrites, checks, repeat.")
        ld = loop_data()
        if ld is None:
            st.info("No rewriting-loop results yet.")
        else:
            st.markdown(f"**The experiment:** {ld['n']} LLM-written paragraphs (5 from our first draft, 5 from "
                        f"GPT-written sections of other papers), revised {ld['rounds']} rounds each, two ways from "
                        f"the same start: a plain *\"make it sound more human\"* prompt, and detector-guided "
                        "feedback naming the exact problems.")
            c = ld["curve"]
            cols = st.columns(2)
            for col, name in ((cols[0], NAIVE_LABEL), (cols[1], GUIDED_LABEL)):
                col.metric(name, f"{c[name].iloc[-1]:.0f}",
                           f"{c[name].iloc[-1] - c[name].iloc[0]:+.0f} from {c[name].iloc[0]:.0f}",
                           delta_color="inverse")
            st.markdown("**Average score after each round** (lower = more human)")
            st.line_chart(c, x_label="Round", y_label="Mean AI-likeness score", color=colours(c))
            st.dataframe(ld["table"], hide_index=True)
            st.caption(f"The plain prompt plateaus: it rewords but keeps the same structure. The detector-guided "
                       "loop changes the structure and keeps improving.")
            if len(ld["rejections"]):
                with st.expander("Why rewrites were rejected"):
                    st.dataframe(ld["rejections"], hide_index=True)
                    st.caption("\"Score went up\" means the rewrite read more AI-like than the previous version, so "
                               "the previous version was kept.")

            st.markdown("#### :material/timeline: Follow one paragraph round by round")
            p = ld["log"][ld["log"].iteration == 0].drop_duplicates("pid").sort_values("score", ascending=False)
            pick = st.selectbox("Paragraph", list(p.pid), format_func=para_label, key="det_loop_pid")
            chart, steps = paragraph_trajectory(ld["log"], pick)
            st.line_chart(chart, x_label="Round", y_label="AI-likeness score", color=colours(chart))
            st.dataframe(steps, hide_index=True)

            un = loop_data("loop_log_v1_unguarded.csv")
            if un is not None:
                with st.expander("What went wrong first: the loop learned to game the detector"):
                    st.markdown(
                        f"Our first run had no fluency guard. The detector-guided score fell to "
                        f"**{un['curve'][GUIDED_LABEL].iloc[-1]:.0f}**, but by chopping sentences into fragments "
                        "(*\"Competence is judged similarly. Education influences these judgments. Trustworthiness "
                        "does too.\"*): technically varied sentence lengths, but worse writing. A measure that "
                        "becomes a target stops being a good measure (Goodhart's law).")
                    st.markdown("We added a **fluency guard**, calibrated on real papers (93% of real passages pass "
                                "it): no fragments under 4 words, no runs of short sentences. The results above "
                                "are with the guard on.")
                    st.line_chart(un["curve"], x_label="Round", y_label="Mean score (first run, no guard)", color=colours(un["curve"]))

            fp = full_paper_data()
            if fp is not None and fp["rounds"] is not None:
                st.markdown("#### :material/description: The same loop on the whole paper")
                st.caption(f"Every prose paragraph of the {FIRST.lower()} scoring 35 or more got up to 3 rounds. "
                           "Tables and the research questions were never sent to the model.")
                st.line_chart(fp["rounds"], x_label="Round", y_label="Mean AI-likeness score", color=[look.HUMAN])

    # ---------------- 3 before/after
    with tabs[3]:
        st.caption("Criterion 4: same content, the dry LLM version and the revised version side by side. "
                   "Green = added, struck through = removed.")
        fp = full_paper_data()
        mode = st.radio("Show", ["Whole paper: first draft vs final paper", "Rewriting experiment: three versions"],
                        horizontal=True, key="det_ba_mode")
        if mode.startswith("Whole") and fp is not None:
            s = fp["scored"]
            cols = st.columns(3)
            cols[0].metric(f"{FIRST}, mean score", f"{s.v0_score.mean():.0f}")
            cols[1].metric(f"{FINAL}, mean score", f"{s.v3_score.mean():.0f}",
                           f"{s.v3_score.mean() - s.v0_score.mean():+.0f}", delta_color="inverse")
            cols[2].metric("Paragraphs rewritten", f"{len(fp['revised'])} of {len(fp['df'])}")
            st.dataframe(fp["by_section"], hide_index=True)
            if len(fp["revised"]):
                rv = fp["revised"].sort_values("v0_score", ascending=False)
                pick = st.selectbox("Paragraph", list(rv.pid), key="det_fp_pid",
                                    format_func=lambda x: f"{rv[rv.pid == x].section.iloc[0].replace('_', ' ').title()}"
                                                          f" · {x} · {rv[rv.pid == x].v0_score.iloc[0]:.0f} → "
                                                          f"{rv[rv.pid == x].v3_score.iloc[0]:.0f}")
                r = rv[rv.pid == pick].iloc[0]
                cols = st.columns(2, gap="large")
                with cols[0]:
                    look.paper(FIRST, clean(r.v0_text), r.v0_score)
                with cols[1]:
                    look.paper(FINAL, clean(r.v3_text), r.v3_score)
                with st.expander("Highlight what changed"):
                    st.markdown(word_diff(clean(r.v0_text), clean(r.v3_text)))
                if _count_terms(clean(r.v3_text).lower(), HEDGES) < _count_terms(clean(r.v0_text).lower(), HEDGES):
                    st.warning("This rewrite removed hedge words. Check it does not now overstate the claim.",
                               icon=":material/warning:")
            if fp["final_md"]:
                with st.container(horizontal=True):
                    st.download_button(f"Download {FINAL.lower()}", fp["final_md"].encode("utf-8"),
                                       file_name="final_paper.md", mime="text/markdown", type="primary",
                                       icon=":material/download:", key="det_dl_final")
                    if fp["first_md"]:
                        st.download_button(f"Download {FIRST.lower()}", fp["first_md"].encode("utf-8"),
                                           file_name="first_draft.md", mime="text/markdown", key="det_dl_first")
                with st.expander(f"Read the whole {FINAL.lower()}"):
                    st.markdown(fp["final_md"])
        elif mode.startswith("Whole"):
            st.info("The whole-paper rewrite has not been run yet.")
        else:
            ld = loop_data()
            if ld is None:
                st.info("No rewriting-loop results yet.")
            else:
                g = ld["log"]
                first = g[g.iteration == 0].drop_duplicates(["pid", "condition"]).set_index(["pid", "condition"])
                last = g[g.iteration == ld["rounds"]].set_index(["pid", "condition"])
                pids = sorted(set(g.pid), key=lambda x: -(first.loc[(x, "guided")].score - last.loc[(x, "guided")].score))
                pick = st.selectbox("Paragraph", pids, format_func=para_label, key="det_ba_pid")
                versions = [("Original", first.loc[(pick, "guided")]),
                            (f"{NAIVE_LABEL}, after {ld['rounds']} rounds", last.loc[(pick, "naive")]),
                            (f"{GUIDED_LABEL}, after {ld['rounds']} rounds", last.loc[(pick, "guided")])]
                cols = st.columns(3, gap="medium")
                for col, (title, row) in zip(cols, versions):
                    with col:
                        look.paper(title, clean(row.text), row.score)
                with st.expander("Highlight what the detector-guided rewrite changed"):
                    st.markdown(word_diff(clean(versions[0][1].text), clean(versions[2][1].text)))

    # ---------------- 4 human test (only once results exist)
    if he is not None:
        with tabs[4]:
            st.caption("Criterion 3: people saw mixed real and generated paragraphs on the same topic and guessed "
                       "which was which. 50% means they could not tell.")
            res = he["results"]
            overall = res.iloc[0]
            st.metric("How often people spotted the generated text correctly", f"{overall.accuracy:.0%}",
                      help=f"95% interval {overall.ci95_low:.0%}-{overall.ci95_high:.0%}, {int(overall.n)} judgements")
            st.dataframe(res, hide_index=True)
            pi = he["per_item"]
            if pi is not None and "detector_score" in pi:
                rho = pi[["detector_score", "share_said_generated"]].corr(method="spearman").iloc[0, 1]
                st.caption(f"Detector vs people: correlation {rho:.2f} between an item's detector score and the share "
                           "of people who called it generated.")
            rs = he["reasons"]
            if rs is not None and len(rs):
                st.markdown("#### What helped people decide")
                for cond, sub in rs.groupby("condition"):
                    with st.expander(f"{cond.replace('_', ' ')} paragraphs ({len(sub)} answers)"):
                        st.dataframe(sub.drop(columns=[c for c in ("condition",) if c in sub]), hide_index=True)
