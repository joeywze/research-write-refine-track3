# Research development

Maintained scripts from the research and pilot-generation workstreams:

| Script | Purpose | Execution effects |
|---|---|---|
| `collect_emnlp.py` | Collect EMNLP 2025 metadata from ACL Anthology | Makes network requests and writes corpus workbooks |
| `sample_papers.py` | Draw the original seeded ten-paper sample | Replaces the sample CSV; do not rerun against a reviewed dataset without preserving it |
| `generate_ai_sections.py` | Generate pilot sections from titles and abstracts | Makes paid API calls, saves/resumes a separate pilot output |

Run these from the repository root using `python src/research/SCRIPT.py`. They are executable scripts, not side-effect-free libraries; do not import them just to discover functionality. Their input/output paths resolve against the repository, not the shell's current directory.

The [notebooks](../../notebooks/) contain corpus mapping, SentenceTransformer embeddings, UMAP/HDBSCAN clustering, abstract extraction and full-text evidence-window analysis. The [research documentation](../../docs/research/README.md) contains the reviewed evidence, counterevidence, candidate gap, proposed study and V0.

This organisation does not add an arbitrary-topic search or automatically approved research-package workflow. The original abstract-generation corpus is for exploratory style analysis; it is separate from the evidence-grounded case-study V0.

Previous locations: `emnlp-literature/collect_emnlp.py`, `src/sample_papers.py`, `src/generate_ai_sections.py`. The last two paths remain compatibility launchers.
