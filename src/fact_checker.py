# --------------------------------------------------
# IMPORTS
# --------------------------------------------------

# Standard Python libraries
import re
from pathlib import Path
import os


# Data processing
import pandas as pd

# Natural language processing
import nltk
from nltk.tokenize import sent_tokenize

# Evidence matching
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# API
from dotenv import load_dotenv

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FACTS_FILE = PROJECT_ROOT / "data" / "facts" / "master_facts.xlsx"

# Export intermediate files for debugging.
SAVE_INTERMEDIATE = False

# --------------------------------------------------
# LOAD FACT DATABASE
# --------------------------------------------------

df = pd.read_excel(FACTS_FILE, sheet_name="Master")

print(f"Loaded {len(df)} evidence records from Master.")

# --------------------------------------------------
# LOAD RESEARCH PAPER
# --------------------------------------------------

DRAFT_FILE = (
    PROJECT_ROOT
    / "docs"
    / "part_a_research_development"
    / "draft_v0.md"
)

if not DRAFT_FILE.exists():
    raise FileNotFoundError(
        f"Research paper not found: {DRAFT_FILE}"
    )

draft_text = DRAFT_FILE.read_text(encoding="utf-8")

print(f"Loaded Draft V0 ({len(draft_text.split())} words).")

# --------------------------------------------------
# SENTENCE EXTRACTION
# --------------------------------------------------

nltk.download("punkt_tab", quiet=True)


def extract_sentences(text):
    """Extract sentences while removing basic Markdown formatting."""

    cleaned_lines = []
    in_references = False

    for line in text.splitlines():
        stripped = line.strip()

        if re.match(r"^#{1,6}\s+References\s*$", stripped, re.I):
            in_references = True

        if in_references:
            continue

        if stripped.startswith("#") or stripped.startswith("|"):
            continue

        if re.fullmatch(r"\d+(?:\.\d+)*\.?", stripped):
            continue

        cleaned_lines.append(stripped)

    paragraphs = []
    current_paragraph = []

    for line in cleaned_lines:
        if not line:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
        else:
            current_paragraph.append(line)

    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    sentences = []

    for paragraph in paragraphs:
        for sentence in sent_tokenize(paragraph):
            sentence = sentence.strip()

            if not sentence:
                continue

            if re.fullmatch(r"\d+(?:\.\d+)*\.", sentence):
                continue

            sentences.append(sentence)

    return sentences

sentences = extract_sentences(draft_text)

print(f"Extracted {len(sentences)} candidate sentences.")


# --------------------------------------------------
# PREPARE EXTRACTED SENTENCES
# --------------------------------------------------

OUTPUT_DIR = PROJECT_ROOT / "results" / "fact_checking"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sentences_df = pd.DataFrame({
    "sentence_id": [
        f"S{i:03d}" for i in range(1, len(sentences) + 1)
    ],
    "sentence": sentences,
    "claim_type": [""] * len(sentences),
})

if SAVE_INTERMEDIATE:
    SENTENCES_FILE = OUTPUT_DIR / "draft_v0_sentences.csv"

    sentences_df.to_csv(
        SENTENCES_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Saved extracted sentences to {SENTENCES_FILE.name}")

# --------------------------------------------------
# BASELINE CLAIM CLASSIFICATION
# --------------------------------------------------

def classify_sentence(sentence):
    text = sentence.lower().strip()

    # Research questions are not factual claims.
    if text.endswith("?"):
        return "OTHER"

    # Existing research and published findings.

    factual_patterns = [
        # Academic citations
        r"\b(?:19|20)\d{2}\b",
        r"\bet al\.",

        # References to existing literature
        r"\bprior (?:work|research|studies)\b",
        r"\bprevious (?:research|studies|findings)\b",
        r"\bexisting (?:research|literature|studies)\b",
        r"\bpublished (?:research|studies|findings)\b",

        # Reporting findings from previous research
        r"\b(?:researchers|authors|studies)\s+"
        r"(?:found|reported|evaluated|demonstrated|showed|identified)\b",

        # References to research results
        r"\b(?:the study|the paper|the authors)\s+"
        r"(?:reports|finds|demonstrates|evaluates|examines|investigates)\b",
    ]

    # Proposed study design and methodology.
    proposed_patterns = [
        r"\bwe propose\b",
        r"\bwe plan\b",
        r"\bwe will\b",
        r"\bwill be\b",
        r"\bthe proposed\b",
        r"\bthe pilot\b",
        r"\bthe study will\b",
        r"\bthe protocol\b",
        r"\bthe analysis\b",
        r"\bthe design\b",
        r"\bthe language pair\b",
        r"\bthe item source\b",
        r"\bthe evaluation\b",
        r"\bthe experiment\b",
        r"\beach response\b",
        r"\beach item\b",
        r"\bwould be\b",
        r"\bshould be\b",
        r"\bnot yet selected\b",
        r"\bnot yet finalised\b",
        r"\bremains unresolved\b",
    ]

    # Prioritise factual claims to avoid missing
    # literature statements containing proposed language.
    if any(re.search(pattern, text) for pattern in factual_patterns):
        return "FACTUAL"

    if any(re.search(pattern, text) for pattern in proposed_patterns):
        return "PROPOSED"

    return "OTHER"


sentences_df["predicted_type"] = sentences_df["sentence"].apply(
    classify_sentence
)

print("\nBaseline classification results:")
print(sentences_df["predicted_type"].value_counts())

# --------------------------------------------------
# IDENTIFY ACL ANTHOLOGY CITATIONS IN DRAFT
# --------------------------------------------------

citation_pattern = (
    r"(?:19|20)\d{2}\."
    r"[a-z][a-z0-9-]*\."
    r"\d+"
)

cited_paper_ids = set(
    re.findall(citation_pattern, draft_text)
)

available_paper_ids = set(
    df["paper_id"].astype(str).str.strip()
)

matched_papers = cited_paper_ids & available_paper_ids
missing_papers = cited_paper_ids - available_paper_ids

print(
    f"Citation matching: {len(matched_papers)} matched, "
    f"{len(missing_papers)} missing from Master."
)


# --------------------------------------------------
# RETRIEVE EVIDENCE FOR CITED PAPERS
# --------------------------------------------------

cited_evidence = df[
    df["paper_id"].astype(str).str.strip().isin(matched_papers)
].copy()

print(
    f"Retrieved {len(cited_evidence)} evidence records "
    f"from {len(matched_papers)} cited papers."
)

if SAVE_INTERMEDIATE:
    EVIDENCE_FILE = (
        OUTPUT_DIR / "draft_v0_cited_evidence.csv"
    )

    cited_evidence.to_csv(
        EVIDENCE_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Saved cited evidence to {EVIDENCE_FILE.name}")

# --------------------------------------------------
# TF-IDF EVIDENCE MATCHING
# --------------------------------------------------

# Prepare evidence text for similarity matching.
evidence_texts = (
    cited_evidence["factual_claim"].fillna("").astype(str)
    + " "
    + cited_evidence["evidence_quote"].fillna("").astype(str)
).tolist()

vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2)
)

evidence_vectors = vectorizer.fit_transform(evidence_texts)


def find_relevant_evidence(sentence, paper_id=None, top_k=3):
    """
    Retrieve the most relevant evidence records using TF-IDF.

    If a paper ID is supplied, restrict retrieval to that paper.
    Similarity indicates textual relevance, not factual accuracy.
    """

    clean_sentence = re.sub(
        r"https?://\S+", "", sentence
    ).strip()

    sentence_vector = vectorizer.transform([clean_sentence])

    similarities = cosine_similarity(
        sentence_vector, evidence_vectors
    )[0]

    candidate_indices = range(len(cited_evidence))

    if paper_id is not None:
        candidate_indices = [
            i for i in candidate_indices
            if str(cited_evidence.iloc[i]["paper_id"]).strip()
            == paper_id
        ]

    ranked_indices = sorted(
        candidate_indices,
        key=lambda i: similarities[i],
        reverse=True
    )[:top_k]

    matches = []

    for index in ranked_indices:
        record = cited_evidence.iloc[index]

        matches.append({
            "claim_id": record["claim_id"],
            "paper_id": record["paper_id"],
            "factual_claim": record["factual_claim"],
            "evidence_quote": record["evidence_quote"],
            "verification": record["verification"],
            "similarity": round(float(similarities[index]), 4)
        })

    return matches


def extract_paper_ids(text):
    """Extract official ACL Anthology paper IDs from text."""

    return sorted(set(re.findall(citation_pattern, text)))

# --------------------------------------------------
# CREATE PARAGRAPH-LEVEL CITATION MAP
# --------------------------------------------------

def extract_paragraphs(text):
    """Extract paragraphs and their ACL Anthology citations."""

    records = []
    current_lines = []
    in_references = False

    def add_paragraph():
        if not current_lines:
            return

        paragraph = " ".join(current_lines).strip()

        if paragraph:
            paper_ids = extract_paper_ids(paragraph)

            records.append({
                "paragraph_id": f"P{len(records) + 1:03d}",
                "paragraph": paragraph,
                "paper_ids": "; ".join(paper_ids),
                "number_of_papers": len(paper_ids)
            })

    for line in text.splitlines():
        stripped = line.strip()

        if re.match(r"^#{1,6}\s+References\s*$", stripped, re.I):
            in_references = True

        if in_references:
            continue

        if not stripped or stripped.startswith(("#", "|")):
            add_paragraph()
            current_lines = []
            continue

        current_lines.append(stripped)

    add_paragraph()

    return pd.DataFrame(records)



paragraph_df = extract_paragraphs(draft_text)

print(
    f"Extracted {len(paragraph_df)} paragraphs; "
    f"{(paragraph_df['number_of_papers'] > 0).sum()} contain paper IDs."
)

if SAVE_INTERMEDIATE:
    PARAGRAPH_FILE = (
        OUTPUT_DIR / "draft_v0_paragraph_citations.csv"
    )

    paragraph_df.to_csv(
        PARAGRAPH_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Saved paragraph citations to {PARAGRAPH_FILE.name}")


# --------------------------------------------------
# EXTRACT MARKDOWN TABLE ROWS
# --------------------------------------------------

def extract_table_rows(text):
    """Extract Markdown table rows before the References section."""

    records = []

    for line in text.splitlines():
        stripped = line.strip()

        # Stop at the References section.
        if re.match(r"^#{1,6}\s+References\s*$", stripped, re.I):
            break

        # Skip non-table lines.
        if not stripped.startswith("|"):
            continue

        cells = [
            cell.strip()
            for cell in stripped.strip("|").split("|")
        ]

        # Skip Markdown separator rows.
        if all(
            re.fullmatch(r":?-{3,}:?", cell or "")
            for cell in cells
        ):
            continue

        records.append({
            "table_row_id": f"T{len(records) + 1:03d}",
            "row_text": " | ".join(cells),
            "paper_ids": "; ".join(extract_paper_ids(stripped))
        })

    return pd.DataFrame(
        records,
        columns=["table_row_id", "row_text", "paper_ids"]
    )


table_df = extract_table_rows(draft_text)

print(f"Extracted {len(table_df)} Markdown table rows.")

if SAVE_INTERMEDIATE:
    TABLE_FILE = OUTPUT_DIR / "draft_v0_table_rows.csv"

    table_df.to_csv(
        TABLE_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Saved Markdown table rows to {TABLE_FILE.name}")

# --------------------------------------------------
# EXTRACT LITERATURE COMPARISON ROWS
# --------------------------------------------------

def extract_literature_rows(table_df):
    """Identify literature comparison rows from Markdown tables."""

    records = []

    for _, row in table_df.iterrows():
        cells = row["row_text"].split(" | ")

        # Literature comparison rows contain three columns.
        if len(cells) != 3:
            continue

        study, factual_statement, proposed_extension = cells

        # Identify the literature comparison table by its header.
        if (
            study.strip().lower() == "study"
            or factual_statement.strip().lower() == "existing evidence"
        ):
            continue

        # Require a publication year in the study column.
        if not re.search(r"\b(?:19|20)\d{2}\b", study):
            continue

        records.append({
            "table_row_id": row["table_row_id"],
            "study": study,
            "factual_statement": factual_statement,
            "proposed_extension": proposed_extension,
            "paper_ids": row["paper_ids"],
            "claim_type": "FACTUAL"
        })

    return pd.DataFrame(
        records,
        columns=[
            "table_row_id",
            "study",
            "factual_statement",
            "proposed_extension",
            "paper_ids",
            "claim_type"
        ]
    )


literature_rows = extract_literature_rows(table_df)

print(f"Extracted {len(literature_rows)} literature comparison rows.")

if SAVE_INTERMEDIATE:
    LITERATURE_FILE = (
        OUTPUT_DIR / "draft_v0_literature_table_claims.csv"
    )

    literature_rows.to_csv(
        LITERATURE_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Saved literature comparison rows to {LITERATURE_FILE.name}")

# --------------------------------------------------
# LOAD PILOT FACTUAL CLAIMS
# --------------------------------------------------

PILOT_CLAIMS_FILE = (
    PROJECT_ROOT
    / "data"
    / "facts"
    / "pilot"
    / "draft_v0_atomic_claims.csv"
)

atomic_df = pd.read_csv(
    PILOT_CLAIMS_FILE,
    keep_default_na=False
)

print(f"Loaded {len(atomic_df)} pilot factual claims.")

# --------------------------------------------------
# MATCH ATOMIC CLAIMS TO MASTER EVIDENCE
# --------------------------------------------------

def match_claims_to_evidence(claims_df, top_k=3):
    """Retrieve relevant evidence for each factual claim."""

    results = []

    for _, draft_claim in claims_df.iterrows():
        matches = find_relevant_evidence(
            sentence=draft_claim["claim"],
            paper_id=draft_claim["paper_id"],
            top_k=top_k
        )

        for rank, match in enumerate(matches, start=1):
            source_record = cited_evidence[
                cited_evidence["claim_id"] == match["claim_id"]
            ].iloc[0]

            results.append({
                "draft_claim_id": draft_claim["draft_claim_id"],
                "draft_claim": draft_claim["claim"],
                "paper_id": draft_claim["paper_id"],
                "evidence_rank": rank,
                "evidence_claim_id": match["claim_id"],
                "evidence_claim": match["factual_claim"],
                "evidence_quote": match["evidence_quote"],
                "page": source_record["page"],
                "verification": match["verification"],
                "similarity": match["similarity"]
            })

    return pd.DataFrame(results)


matching_df = match_claims_to_evidence(atomic_df)

MATCHING_FILE = (
    OUTPUT_DIR / "draft_v0_evidence_matches.csv"
)

matching_df.to_csv(
    MATCHING_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(
    f"Matched {len(atomic_df)} pilot claims "
    f"to {len(matching_df)} evidence records."
)

# --------------------------------------------------
# LOAD PILOT VERIFICATION RESULTS
# --------------------------------------------------

PILOT_VERIFICATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "facts"
    / "pilot"
    / "draft_v0_pilot_verification.csv"
)

verification_df = pd.read_csv(
    PILOT_VERIFICATION_FILE,
    keep_default_na=False
)

# Ensure the verification results match the pilot claims.
expected_ids = set(atomic_df["draft_claim_id"])
verified_ids = set(verification_df["draft_claim_id"])

if expected_ids != verified_ids:
    raise ValueError(
        "Pilot verification IDs do not match the pilot claims."
    )

if verification_df["draft_claim_id"].duplicated().any():
    raise ValueError(
        "Duplicate draft claim IDs found in pilot verification."
    )

print(f"Loaded {len(verification_df)} pilot verification results.")
print(verification_df["verification_status"].value_counts())

# --------------------------------------------------
# CALCULATE EVIDENCE-GROUNDING SCORE
# --------------------------------------------------

def calculate_grounding_score(results_df):
    """Calculate the percentage of fully supported claims."""

    total = len(results_df)

    supported = (
        results_df["verification_status"] == "SUPPORTED"
    ).sum()

    score = (supported / total * 100) if total > 0 else 0.0

    return total, supported, score


total_claims, supported_claims, grounding_score = (
    calculate_grounding_score(verification_df)
)

print("\n" + "=" * 50)
print("DRAFT V0 — PILOT EVIDENCE-GROUNDING SCORE")
print("=" * 50)

print(f"Total claims assessed: {total_claims}")
print(f"Fully supported claims: {supported_claims}")
print(f"Evidence-grounding score: {grounding_score:.1f}%")

print("\nNote: Manually assessed pilot claims only.")
print("This is not the factual accuracy score of the full paper.")


# --------------------------------------------------
# CHECK OPENAI API CONFIGURATION
# --------------------------------------------------

env_path = PROJECT_ROOT / ".env"

print(f"\nEnvironment file exists: {env_path.is_file()}")

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if api_key and api_key.strip():
    print("\nOpenAI API key configuration: FOUND")
else:
    print("\nOpenAI API key configuration: NOT FOUND")
