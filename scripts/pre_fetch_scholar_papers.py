"""Fetches the group's publication list from Google Scholar and writes it,
formatted in Vancouver style, into papers/index.qmd between the
`<!-- scholar:auto:start -->` / `<!-- scholar:auto:end -->` markers.

Google Scholar has no public API, so this scrapes the public profile pages.
Scholar occasionally rate-limits or blocks automated requests; if that
happens this script leaves the existing content untouched instead of
wiping the section.
"""
import os
import re
import sys
import time
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

SCHOLAR_USER = "m67uDzwAAAAJ"
BASE_URL = "https://scholar.google.com/citations"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
PAGE_SIZE = 20
REQUEST_DELAY_SECONDS = 1.2
NOBILIARY_PARTICLES = {"de", "del", "la", "van", "von", "der", "den", "di", "da", "dos", "le", "el"}
START_MARKER = "<!-- scholar:auto:start -->"
END_MARKER = "<!-- scholar:auto:end -->"


def fetch_listing_page(cstart: int) -> list:
    params = {
        "hl": "es",
        "user": SCHOLAR_USER,
        "view_op": "list_works",
        "sortby": "pubdate",
        "cstart": cstart,
        "pagesize": PAGE_SIZE,
    }
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = []
    for tr in soup.select("tr.gsc_a_tr"):
        link = tr.select_one("a.gsc_a_at")
        if not link:
            continue
        href = link.get("href", "")
        match = re.search(r"citation_for_view=([^&]+)", href)
        if not match:
            continue
        rows.append({
            "citation_id": match.group(1),
            "title": link.get_text(strip=True),
        })
    return rows


def fetch_all_listings() -> list:
    all_rows = []
    cstart = 0
    while True:
        rows = fetch_listing_page(cstart)
        all_rows.extend(rows)
        if len(rows) < PAGE_SIZE:
            break
        cstart += PAGE_SIZE
        time.sleep(REQUEST_DELAY_SECONDS)
    return all_rows


def fetch_detail(citation_id: str) -> dict:
    params = {
        "hl": "es",
        "user": SCHOLAR_USER,
        "view_op": "view_citation",
        "sortby": "pubdate",
        "citation_for_view": citation_id,
    }
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    fields = {}
    for row in soup.select("#gsc_oci_table .gs_scl"):
        field_el = row.select_one(".gsc_oci_field")
        value_el = row.select_one(".gsc_oci_value")
        if field_el and value_el:
            fields[field_el.get_text(strip=True)] = value_el.get_text(" ", strip=True)

    title_link = soup.select_one("a.gsc_oci_title_link")
    external_url = title_link.get("href") if title_link else None

    title_el = soup.select_one("#gsc_oci_title")
    full_title = title_el.get_text(" ", strip=True) if title_el else None

    scholar_articles = fields.get("Artículos de Google Académico", "")
    journal_from_scholar_blurb = None
    blurb_match = re.search(r"-\s*([^,]+),\s*\d{4}\s*$", scholar_articles.split("Artículos relacionados")[0].strip())
    if blurb_match:
        journal_from_scholar_blurb = blurb_match.group(1).strip()

    return {
        "fields": fields,
        "external_url": external_url,
        "full_title": full_title,
        "journal_from_blurb": journal_from_scholar_blurb,
    }


def extract_doi(url: str) -> str:
    if not url:
        return None
    match = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", url)
    if not match:
        return None
    return match.group(0).rstrip(".,;)")


def normalize_hyphen(text: str) -> str:
    return text.replace("‐", "-").replace("‑", "-")


def to_vancouver_author(full_name: str) -> str:
    full_name = normalize_hyphen(full_name).strip()
    tokens = full_name.split()
    if not tokens:
        return full_name

    surname_tokens = [tokens[-1]]
    remaining = tokens[:-1]
    while remaining and remaining[-1].lower() in NOBILIARY_PARTICLES:
        surname_tokens.insert(0, remaining.pop())

    initials = "".join(t[0].upper() for t in remaining if t)
    surname = " ".join(surname_tokens)
    return f"{surname} {initials}".strip()


def format_authors(authors_field: str) -> str:
    names = [a.strip() for a in authors_field.split(",") if a.strip()]
    vancouver_names = [to_vancouver_author(n) for n in names]
    if len(vancouver_names) > 6:
        return ", ".join(vancouver_names[:6]) + ", et al"
    return ", ".join(vancouver_names)


def format_entry(listing: dict, detail: dict) -> str:
    fields = detail["fields"]
    authors = format_authors(fields.get("Autores", ""))
    title = normalize_hyphen(detail.get("full_title") or listing["title"]).rstrip(".")
    journal = (
        fields.get("Origen")
        or fields.get("Fuente")
        or fields.get("Conferencia")
        or fields.get("Revista")
        or detail.get("journal_from_blurb")
    )
    volume = fields.get("Volumen")
    issue = fields.get("Número")
    pages = fields.get("Páginas")
    pub_date = fields.get("Fecha de publicación", "")
    year = pub_date.split("/")[0] if pub_date else ""

    citation = f"{authors}. {title}."
    if journal:
        citation += f" _{journal}_."
    if year:
        vol_issue = f"{volume}({issue})" if volume and issue else (volume or "")
        citation += f" {year}"
        if vol_issue or pages:
            citation += f";{vol_issue}"
        if pages:
            citation += f":{pages}"
        citation += "."

    doi = extract_doi(detail.get("external_url"))
    if doi:
        citation += f' doi: [{doi}](https://doi.org/{doi}){{target="_blank" rel="noopener"}}'
    elif detail.get("external_url"):
        citation += f' [Ver publicación]({detail["external_url"]}){{target="_blank" rel="noopener"}}'

    return citation, year


def generate_markdown() -> str:
    listings = fetch_all_listings()
    entries_by_year = defaultdict(list)

    for listing in listings:
        try:
            detail = fetch_detail(listing["citation_id"])
        except requests.RequestException as exc:
            print(f"  WARN: no se pudo obtener el detalle de '{listing['title']}': {exc}", file=sys.stderr)
            continue
        citation, year = format_entry(listing, detail)
        entries_by_year[year or "s.f."].append(citation)
        time.sleep(REQUEST_DELAY_SECONDS)

    md = ""
    for year in sorted(entries_by_year.keys(), reverse=True):
        md += f"# {year}\n\n"
        for citation in entries_by_year[year]:
            md += f"- {citation}\n\n"
    return md


def write_into_file(markdown: str, destination_path: str) -> None:
    with open(destination_path, "r", encoding="utf-8") as file:
        content = file.read()

    start = content.find(START_MARKER)
    end = content.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No se encontraron los marcadores {START_MARKER}/{END_MARKER} en {destination_path}")

    new_content = (
        content[: start + len(START_MARKER)]
        + "\n\n"
        + markdown
        + content[end:]
    )

    with open(destination_path, "w", encoding="utf-8") as file:
        file.write(new_content)


if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    if not os.getenv("QUARTO_PROJECT_RENDER_ALL") and not os.getenv("SCHOLAR_SYNC_FORCE"):
        print("Omitiendo sincronizacion con Google Scholar (no es un render completo del proyecto).")
        sys.exit()

    OUTPUT_FILENAME = "papers/index.qmd"

    print("Descargando listado de publicaciones desde Google Scholar...")
    try:
        markdown = generate_markdown()
    except requests.RequestException as exc:
        print(f"ERROR: no se pudo sincronizar con Google Scholar ({exc}). Se conserva el contenido existente.", file=sys.stderr)
        sys.exit()

    if not markdown.strip():
        print("ADVERTENCIA: Google Scholar no devolvio publicaciones (posible bloqueo/CAPTCHA). Se conserva el contenido existente.", file=sys.stderr)
        sys.exit()

    write_into_file(markdown, OUTPUT_FILENAME)
    print(f"Listo. Publicaciones escritas en {OUTPUT_FILENAME}.")
