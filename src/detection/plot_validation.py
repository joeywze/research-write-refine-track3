"""Slide chart: detector score distributions for real vs generated text."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "detection"
oof = pd.read_csv(OUT / "detector_oof_predictions.csv")
body = pd.read_csv(OUT / "heldout_fulltext_passages.csv")
para = pd.read_csv(OUT / "paragraph_scores.csv")
run0 = sorted(para.run.unique())[-1]
v0 = para[(para.run == run0) & para.version.str.startswith("V0")]
val = json.loads((OUT / "detector_validation.json").read_text())
ho = json.loads((OUT / "heldout_fulltext.json").read_text())

groups = [
    ("Real EMNLP abstracts", oof[oof.label == 0].p_stylo * 100, "#2a78d6"),
    ("Real EMNLP body text\n(held out, 18 papers)", body.score, "#2a78d6"),
    ("GPT-generated paragraphs", oof[oof.label == 1].p_stylo * 100, "#eb6834"),
    ("Our draft V0", v0.score, "#1baf7a"),
]
fig, ax = plt.subplots(figsize=(10, 4.6), dpi=200)
for i, (name, s, c) in enumerate(groups[::-1]):
    bp = ax.boxplot([s], positions=[i], orientation="horizontal", widths=0.5, patch_artist=True,
                    showfliers=False, medianprops=dict(color="white", lw=2),
                    whiskerprops=dict(color=c, lw=1.5), capprops=dict(color=c, lw=1.5))
    bp["boxes"][0].set(facecolor=c, edgecolor=c, alpha=0.9)
    ax.text(101, i, f"median {s.median():.0f}  (n={len(s)})", va="center", fontsize=9, color="#555")
ax.set_yticks(range(len(groups)))
ax.set_yticklabels([g[0] for g in groups[::-1]], fontsize=10)
ax.set_xlim(0, 100)
ax.axvline(50, color="#999", lw=1, ls="--")
ax.set_xlabel("Detector AI-likeness score (0 = reads like real EMNLP prose, 100 = reads like GPT)")
ax.set_title(f"Detector separates real from generated text  -  AUC {val['auc_stylometric_all']:.2f} cross-validated, "
             f"{ho['auc_body_text_heldout']:.2f} on held-out body text", fontsize=11, loc="left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#eee")
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(OUT / "detector_validation.png", bbox_inches="tight")
print("saved", OUT / "detector_validation.png")
