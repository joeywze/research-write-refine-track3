"""Data and display helpers for the Sprint 3 demo site (no Streamlit here, so it can be tested)."""

from collections import Counter, defaultdict, deque
import csv
import difflib
import html
import io
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
BUNDLES = HERE / "bundles"
ROOT = HERE.parent
THRESHOLD = 35
ALL_EMNLP_MEAN = 40.2   # mean unseen-paper score over 1,808 real EMNLP 2025 abstracts
CITATION = re.compile(r"\[\[([A-Za-z][A-Za-z0-9_-]*)\]\]")
CHECK_NAMES = {"fluency guard": "Fluency", "preservation rules": "Facts kept", "no new facts": "No new facts",
               "evidence check": "Evidence", "meaning check": "Meaning", "length and tokens": "Length"}
OUTCOMES = {"revised": ("Rewritten", "success"), "kept original": ("Kept unchanged", "neutral"),
            "held for research": ("Held, needs research", "warning"),
            "held by you": ("Held, needs revision", "warning")}


# ---------------------------------------------------------------- loading
def topics():
    return json.loads((BUNDLES / "index.json").read_text(encoding="utf-8"))["topics"]


def bundle(topic_id):
    return json.loads((BUNDLES / f"{topic_id}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- claim review -> held paragraphs
def held_by_user(b, decisions, reviewed):
    """Paragraph IDs with at least one claim the user marked 'Needs revision' (only if they chose to review)."""
    if not reviewed:
        return set()
    return {c["paragraph_id"] for c in b["claims"] if decisions.get(c["claim_id"]) == "Needs revision"}


def final_view(b, held):
    """Final paper paragraphs and rewrite records after applying the user's holds.

    A held paragraph keeps its first-draft text and score, as the pipeline does for paragraphs that
    need research."""
    v0 = {p["id"]: p for p in b["v0"]["paragraphs"]}
    paragraphs = [dict(v0[p["id"]]) if p["id"] in held else p for p in b["final"]["paragraphs"]]
    records = []
    for r in b["rewrite"]["paragraphs"]:
        r = dict(r)
        if r["paragraph_id"] in held and r["outcome"] != "held for research":
            r.update(outcome="held by you", score_after=r["score_before"])
        records.append(r)
    return paragraphs, records


def mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 1) if values else None


def outcome_counts(records):
    return Counter(r["outcome"] for r in records)


# ---------------------------------------------------------------- text
def plain(text):
    """Text without [[S01]] citation tokens (for display)."""
    text = re.sub(r"\s*(?:\[\[[^\]]+\]\]\s*;?\s*)+", " ", text)
    text = re.sub(r"\s+([.,;:])", r"\1", text)
    return re.sub(r"([.!?])\.", r"\1", text).strip()


def word_diff(before, after):
    """HTML with deleted words struck through and new words highlighted."""
    a, b = plain(before).split(), plain(after).split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(html.escape(" ".join(a[i1:i2])))
            continue
        if i2 > i1:
            out.append(f'<del class="rw-del">{html.escape(" ".join(a[i1:i2]))}</del>')
        if j2 > j1:
            out.append(f'<ins class="rw-ins">{html.escape(" ".join(b[j1:j2]))}</ins>')
    return " ".join(out)


def render_markdown(b, paragraphs):
    """The paper as Markdown, with headings, tables and the original citation links restored."""
    by_id = {p["id"]: p["text"] for p in paragraphs}
    blocks = {x["paragraph_id"]: x for x in b["manifest"]["blocks"]}
    out = []
    for segment in b["manifest"]["layout"]:
        if isinstance(segment, str):
            out.append(segment)
            continue
        pid = segment["paragraph_id"]
        queues = defaultdict(deque)
        for occ in blocks[pid]["citation_occurrences"]:
            queues[occ["source_id"]].append(occ["original_markdown"])
        out.append(CITATION.sub(lambda m: queues[m[1]].popleft() if queues[m[1]] else "", by_id[pid]))
    return "".join(out)


# ---------------------------------------------------------------- the hard case and the checks
def hard_case(records):
    """A paragraph where a content check, not just the score, stopped a rewrite.

    Prefers a check that rejected the rewrite for its own content; otherwise an evidence check that
    could not verify a claim and so refused to pass it (fail closed). A meaning-check verdict that only
    blames a different paragraph is skipped: that is a checker limitation, not a good example."""
    content = ("evidence check", "meaning check", "preservation rules", "no new facts")
    fallback = None
    for r in records:
        pid = r["paragraph_id"]
        for a in r["attempts"]:
            for c in a["checks"] or []:
                if c["check"] not in content or c["status"] == "PASS":
                    continue
                others = set(re.findall(r"\bP\d{3}\b", c.get("reason") or "")) - {pid}
                if c["status"] != "CHECK_ERROR" and not others:
                    return pid
                if c["status"] == "CHECK_ERROR" and c["check"] == "evidence check" and fallback is None:
                    fallback = pid
    return fallback


def accepted_checks(record):
    """[(label, passed)] for the attempt that was kept, or for the last attempt."""
    attempts = record["attempts"]
    chosen = next((a for a in reversed(attempts) if a["accepted"]), attempts[-1] if attempts else None)
    if not chosen:
        return []
    return [(CHECK_NAMES.get(c["check"], c["check"]), c["status"] == "PASS") for c in chosen["checks"] or []
            if c["check"] in CHECK_NAMES]


def plain_verdict(verdict):
    return (verdict or "").replace("rejected by detector:", "score did not drop enough:").replace("rejected by ", "rejected by the ")


# ---------------------------------------------------------------- the colour scale
def scale_html(first, final, band, all_mean=ALL_EMNLP_MEAN):
    """Green-to-red bar (0-100) with markers for the first draft and the final paper, a dashed box
    for the real papers the draft cites, and a tick for the average real EMNLP abstract."""
    def x(v):
        return max(0.0, min(100.0, float(v)))
    parts = ['<div class="rw-scale"><div class="rw-bar"></div>']
    if band and band.get("n"):
        lo, hi = x(band["min"]), x(band["max"])
        parts.append(f'<div class="rw-band" style="left:{lo:.1f}%;width:{max(hi - lo, 1):.1f}%"></div>'
                     f'<div class="rw-bandlab" style="left:{lo}%">Real papers this draft cites ({band["min"]:.0f}–{band["max"]:.0f}, n={band["n"]})</div>')
    parts.append(f'<div class="rw-tick" style="left:{x(all_mean)}%"></div>'
                 f'<div class="rw-ticklab" style="left:{x(all_mean)}%">Average real EMNLP abstract {all_mean:.0f}</div>')
    for label, v, cls in (("First draft", first, "rw-m1"), ("Final paper", final, "rw-m2")):
        if v is not None:
            parts.append(f'<div class="rw-marker {cls}" style="left:{x(v)}%">▼ {label} {v:.0f}</div>')
    parts.append('<div class="rw-ends"><span>0 · least formulaic</span><span>100 · most formulaic</span></div></div>')
    return "".join(parts)


def chip(score):
    if score is None:
        return ""
    tone = "ok" if score < THRESHOLD else ("mid" if score < 60 else "high")
    return f'<span class="rw-chip rw-{tone}">{score:.0f}</span>'


# ---------------------------------------------------------------- downloads
def decisions_csv(b, decisions, reviewed):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["topic", "claim_id", "paragraph_id", "claim", "decision"])
    for c in b["claims"]:
        w.writerow([b["id"], c["claim_id"], c["paragraph_id"], c["claim"],
                    decisions.get(c["claim_id"], "") if reviewed else "not reviewed"])
    return buf.getvalue()


def change_report(b, records, held):
    return json.dumps({"topic": b["id"], "title": b["title"], "source_run": b["source_run"],
                       "held_by_reader": sorted(held), "paragraphs": records,
                       "critic": b["rewrite"]["critic"]}, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- uploads (scored only on the hosted site)
def split_upload(text, min_words=40):
    paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    return [p for p in paras if p and not p.startswith("#") and len(p.split()) >= min_words]


# ---------------------------------------------------------------- rewriting pasted text (local version only)
def env_file_key():
    """OPENAI_API_KEY from a .env file in the repo root (or sprint2_demo/), read directly: no extra package,
    and tolerant of 'export', spaces around '=', quotes and a Windows byte-order mark."""
    for path in (ROOT / ".env", ROOT / "sprint2_demo" / ".env"):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].strip()
            name, sep, value = line.partition("=")
            if sep and name.strip() == "OPENAI_API_KEY":
                value = value.split(" #")[0].strip().strip('"').strip("'")
                if value:
                    return value
    return ""


def live_allowed():
    """(allowed, reason). Rewriting pasted text needs an OpenAI key: in the local version it is read from the
    environment or the repo's .env file; the hosted preview has none, so rewriting stays off there."""
    import os
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        key = env_file_key()
        if key:
            os.environ["OPENAI_API_KEY"] = key
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return True, ""
    return False, ("Rewriting needs an OpenAI API key, so it is switched off in this online preview. Scoring works "
                   "here; to rewrite, run the site locally with your key in the repo's .env file.")


def rewrite_text(text, model_name, attempts=3, min_gain=5.0, call=None):
    """Detector-guided rewrite of one pasted paragraph, with the deterministic checks.

    Each attempt gets the detector's feedback; a candidate counts only if the score drops by at least
    `min_gain` and it keeps every number and citation, keeps its length and has no fragment sentences.
    (Pasted text has no research package, so the evidence and meaning checks of the full pipeline do
    not run.) Returns (best_text or None, best_score, [(attempt, score, verdict)])."""
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "src" / "detection"))
    import rewrite_loop as rl
    model = json.loads((ROOT / "results" / "detection" / "detector_model.json").read_text(encoding="utf-8"))
    if call is None:
        from openai import OpenAI
        client = OpenAI(timeout=90)

        def call(prompt):
            return client.responses.create(model=model_name, input=prompt).output_text.strip()
    start = rl.score(text, model)
    best, best_score, log, note = None, start["score"], [], ""
    for i in range(1, attempts + 1):
        base = best or text
        prompt = rl.GUIDED_PROMPT.format(score=rl.score(base, model)["score"], drivers=rl.drivers_text(rl.score(base, model)),
                                         flagged=rl.flagged_text(rl.score(base, model)), text=base)
        if note:
            prompt += "\n\nAbout your previous attempt: " + note
        try:
            candidate = call(prompt)
        except Exception as error:  # a failed call is a failed attempt
            log.append((i, None, f"model call failed: {type(error).__name__}"))
            continue
        ok, why = rl.content_ok(text, candidate)
        if ok:
            ok, why = rl.fluency_ok(candidate)
        s = rl.score(candidate, model)["score"]
        needed = best_score - (min_gain if best is None else 0.5)
        if ok and s > needed:
            ok, why = False, f"score {s:.0f} did not drop enough"
        log.append((i, s, "kept" if ok else why))
        if ok:
            best, best_score = candidate, s
            if s < THRESHOLD:
                break
            note = f"that version scores {s:.0f}; change sentence structure further, keeping every fact."
        else:
            note = why + ". Change sentence structure, not just punctuation; keep every number and citation."
    return best, best_score, log


# ---------------------------------------------------------------- detector page: latest runs
CLICHE = ("Furthermore, it is important to note that our robust, scalable, and efficient framework may potentially "
          "offer significant improvements. Moreover, these findings highlight the crucial role of careful evaluation, "
          "and they may also suggest promising directions for future research in this rapidly evolving field.")


def example_texts():
    """Pre-loaded texts for 'Try it': a cliched paragraph, the highest-scoring rewritten paragraph of the
    reviewed topic before and after the final run, and a real EMNLP 2025 passage."""
    out = {"A clichéd, LLM-style paragraph": CLICHE}
    b = bundle("cluster7")
    rewritten = [r for r in b["rewrite"]["paragraphs"] if r["outcome"] == "revised"]
    if rewritten:
        r = max(rewritten, key=lambda r: r["score_before"] - r["score_after"])
        v0 = {p["id"]: p["text"] for p in b["v0"]["paragraphs"]}
        final = {p["id"]: p["text"] for p in b["final"]["paragraphs"]}
        sec = r["section"].replace("_", " ")
        out[f"Our first draft ({sec}, {r['paragraph_id']})"] = plain(v0[r["paragraph_id"]])
        out[f"The same paragraph in our final paper"] = plain(final[r["paragraph_id"]])
    real = ROOT / "data" / "human_eval" / "real_passages_curated.csv"
    if real.exists():
        rows = list(csv.DictReader(real.read_text(encoding="utf-8-sig").splitlines()))
        if rows:
            out["A passage from a real EMNLP 2025 paper"] = rows[0]["text"]
    return out


def pipeline_summary():
    """Per-topic totals and the reasons attempts were rejected, across the five final runs."""
    rows, reasons = [], Counter()
    for t in topics():
        b = bundle(t["id"])
        tot = b["rewrite"]["totals"]
        c = b["rewrite"].get("critic") or {}
        rows.append({"Topic": t["title"], "Selected (35+)": tot["selected"], "Rewritten": tot["revised"],
                     "Kept unchanged": tot["kept_original"] - tot.get("held_for_research", 0),
                     "Held for research": tot.get("held_for_research", 0),
                     "Score before": tot["mean_score_before"], "Score after": tot["mean_score_after"],
                     "Reviewer": f"{c.get('review_of_v0', '–')} / {c.get('review_of_final', '–')}"})
        for r in b["rewrite"]["paragraphs"]:
            for a in r["attempts"]:
                failed = [x for x in a["checks"] or [] if x["status"] != "PASS"]
                if failed:
                    reasons[REJECTION_NAMES.get(failed[0]["check"], failed[0]["check"])] += 1
    return rows, reasons


REJECTION_NAMES = {"detector": "Score did not drop by 5", "fluency guard": "Fluency guard (choppy sentences)",
                   "writer": "Repeated an earlier version", "evidence check": "Evidence check",
                   "meaning check": "Meaning check", "preservation rules": "Facts changed",
                   "no new facts": "New facts added", "length and tokens": "Length or citations changed"}


def seeded_rows(summary):
    """Seeded-fault results for display. The two people-judged categories ('clean rewrite' cases marked as
    drift and 'real V3 rewrite', i.e. real rewrites from the Sprint 2 V3 run) are shown as one row."""
    drift = ("clean rewrite", "real V3 rewrite")
    rows = [{"Error type": k[0].upper() + k[1:], "Planted": v["planted"], "Caught": v["caught"]}
            for k, v in summary["by_fault_type"].items() if k not in drift]
    judged = [summary["by_fault_type"][k] for k in drift if k in summary["by_fault_type"]]
    if judged:
        rows.append({"Error type": "Subtle meaning drift (judged by people)",
                     "Planted": sum(v["planted"] for v in judged), "Caught": sum(v["caught"] for v in judged)})
    return rows
