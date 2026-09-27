import time
import requests
import pandas as pd
from bs4 import BeautifulSoup


papers = []
failed_papers = []

TOTAL_PAPERS = 1809

headers = {
    "User-Agent": "Mozilla/5.0"
}


for number in range(1, TOTAL_PAPERS + 1):

    paper_id = f"2025.emnlp-main.{number}"
    paper_url = f"https://aclanthology.org/{paper_id}/"

    print(f"[{number}/{TOTAL_PAPERS}] Collecting {paper_id}...")

    try:
        response = requests.get(
            paper_url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")


        # -------------------------
        # Extract title
        # -------------------------

        title = soup.find("h2", id="title")

        if title:
            title_text = title.get_text(" ", strip=True)
        else:
            title_text = "Not found"


        # -------------------------
        # Extract authors
        # -------------------------

        author_links = soup.select("p.lead a")

        authors = []

        for author in author_links:
            author_name = author.get_text(" ", strip=True)

            if author_name:
                authors.append(author_name)

        if authors:
            authors_text = "; ".join(authors)
        else:
            authors_text = "Not found"


        # -------------------------
        # Extract abstract
        # -------------------------

        abstract_heading = soup.find(
            lambda tag:
                tag.name in ["h2", "h3", "h4", "h5"]
                and tag.get_text(strip=True).lower() == "abstract"
        )

        if abstract_heading:

            abstract = abstract_heading.find_next("span")

            if abstract:
                abstract_text = abstract.get_text(" ", strip=True)
            else:
                abstract_text = "Not found"

        else:
            abstract_text = "Not found"


        # -------------------------
        # Extract PDF URL
        # -------------------------

        pdf_link = soup.find(
            "a",
            href=lambda href:
                href
                and href.endswith(".pdf")
                and paper_id in href
        )

        if pdf_link:
            pdf_url = pdf_link.get("href")
        else:
            pdf_url = "Not found"


        # -------------------------
        # Store paper
        # -------------------------

        paper_data = {
            "paper_id": paper_id,
            "title": title_text,
            "authors": authors_text,
            "abstract": abstract_text,
            "paper_url": paper_url,
            "pdf_url": pdf_url
        }

        papers.append(paper_data)


    except Exception as error:

        print(f"    FAILED: {error}")

        failed_papers.append({
            "paper_id": paper_id,
            "paper_url": paper_url,
            "error": str(error)
        })


    # -------------------------
    # Save progress every 100
    # -------------------------

    if number % 100 == 0:

        progress_df = pd.DataFrame(papers)

        progress_df.to_excel(
            "./data/emnlp_2025_progress.xlsx",
            index=False
        )

        print(
            f"    Progress saved: "
            f"{len(papers)} papers collected so far."
        )


    # Be polite to the website
    time.sleep(0.2)


# -------------------------
# Save final dataset
# -------------------------

df = pd.DataFrame(papers)

output_file = "./data/emnlp_2025_main.xlsx"

df.to_excel(
    output_file,
    index=False
)


# -------------------------
# Save failures, if any
# -------------------------

if failed_papers:

    failed_df = pd.DataFrame(failed_papers)

    failed_df.to_excel(
        "./data/emnlp_2025_failed.xlsx",
        index=False
    )


# -------------------------
# Final report
# -------------------------

print("\n==============================")
print("COLLECTION FINISHED")
print("==============================")

print("Expected papers:", TOTAL_PAPERS)
print("Successfully collected:", len(papers))
print("Failed:", len(failed_papers))
print("Saved to:", output_file)

if failed_papers:
    print(
        "Failure details saved to: "
        "./data/emnlp_2025_failed.xlsx"
    )