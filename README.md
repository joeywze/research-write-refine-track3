# Track 3 — Research Paper Ideation and Writing

This repository contains our group project for **Track 3: Research Paper Ideation and Writing**.

## Project Aim

The goal of this project is to develop a research idea that is grounded in existing published work and produce a research paper draft that reads naturally rather than sounding overly AI-generated.

## What We Will Do

- Review relevant research papers from major AI and NLP conferences.
- Identify research gaps, limitations, and possible extensions.
- Develop a clear and realistic research idea.
- Generate an initial paper draft using an LLM.
- Analyse common patterns found in AI-generated academic writing.
- Build a simple baseline detector using methods such as TF-IDF.
- Improve the paper to make the writing clearer, more natural, and more human-like.

## Project Workflow

```text
Literature Review
      ↓
Research Gap Identification
      ↓
Research Idea Development
      ↓
Draft v0 Generation
      ↓
AI-Writing Detection
      ↓
Writing Analysis
      ↓
Draft Improvement
      ↓
Final Paper
```

## Repository Structure

```
data/          # Data used for the project
emnlp-literature/    # Paper mining and literature review
notebooks/     # Experiments and analysis
src/           # Detection and processing scripts
drafts/        # Draft versions of the paper
results/       # Results, figures and tables

```

## Dataset and Stratified Sampling
30 EMNLP 2025 main-conference papers using equal-allocation stratified sampling: five papers from each of six topic groups. Selection within each eligible group used deterministic SHA-256 ranking with seed 20261006. The original ten papers were excluded and retained as pilot data. Eligibility required abstracts of 90–320 words, 2–9 authors, and an unambiguous keyword-derived topic assignment. These filters restrict the sampling population; topic labels and PDF section availability still require review.
 
## Getting Started

1. Clone this repository.

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

As the project develops, additional setup instructions will be added here.

## Final Deliverables

The project will produce:

- Literature review and research gap analysis
- Proposed research idea
- AI-writing detection experiments
- Analysis of LLM writing patterns
- Final research paper draft

The final paper will follow a standard research structure:

**Abstract · Introduction · Related Work · Methodology · Experiments · Conclusion** 
