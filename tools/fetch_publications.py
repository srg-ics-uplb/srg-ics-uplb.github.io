"""Build data/publications_all.yml from the group leader's BibTeX file.

Keeps only publications with at least one author who is SRG faculty/student
(data/people.yml) or an SRG alumnus (data/alumni.yml), and marks those
authors so the site can show them in bold.

Usage:  .venv/bin/python tools/fetch_publications.py [BIB_URL_OR_PATH]
"""
import datetime
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

import yaml

BIB_URL = "https://jachermocilla.org/publications/jachermocilla-publications.bib"
PDF_BASE = "https://jachermocilla.org/publications/"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "publications_all.yml"

SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}
PARTICLES = {"de", "del", "dela", "la", "delos", "los", "san", "van", "von", "da", "di"}


# --------------------------------------------------------------------- BibTeX
def read_bib(src):
    if re.match(r"https?://", src):
        with urllib.request.urlopen(src, timeout=30) as r:
            return r.read().decode("utf-8")
    return Path(src).read_text(encoding="utf-8")


def parse_bib(text):
    """Minimal BibTeX parser: returns [{'type','key', field: value, ...}] in file order."""
    entries, i = [], 0
    while True:
        m = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(text, i)
        if not m:
            return entries
        entry = {"type": m.group(1).lower(), "key": m.group(2)}
        i = m.end()
        while True:
            fm = re.compile(r"\s*(\w+)\s*=\s*").match(text, i)
            if not fm:
                break
            name, i = fm.group(1).lower(), fm.end()
            if text[i] == "{":
                depth, j = 0, i
                while True:
                    if text[j] == "{":
                        depth += 1
                    elif text[j] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                value, i = text[i + 1 : j], j + 1
            elif text[i] == '"':
                j = text.index('"', i + 1)
                value, i = text[i + 1 : j], j + 1
            else:
                vm = re.compile(r"[^,}\s]+").match(text, i)
                value, i = vm.group(0), vm.end()
            entry[name] = " ".join(value.split())
            cm = re.compile(r"\s*,").match(text, i)
            if cm:
                i = cm.end()
        end = text.index("}", i)
        i = end + 1
        entries.append(entry)


def clean(s):
    """Remove BibTeX grouping braces and use an en dash for page ranges."""
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"(?<=\d)\s*--?\s*(?=\d)", "–", s)
    return " ".join(s.split())


def sentence_title(s):
    """Keep titles as written in the .bib, minus braces.

    ALL-CAPS titles become sentence case; a single word before a colon is kept
    as is, since it is usually a system name or acronym ("BERTUD: Building ...").
    """
    s = clean(s).rstrip(".")
    if s.isupper():
        head, sep, rest = s.partition(": ")
        if sep and " " not in head:
            s = f"{head}: {rest[:1]}{rest[1:].lower()}"
        else:
            s = s[:1] + s[1:].lower()
    return s


# ---------------------------------------------------------------------- names
def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z\- ]", "", s.lower().replace(".", " ")).split()


def split_bib_name(raw):
    """Return (display 'First Last', surname tokens, first initial)."""
    raw = clean(raw)
    if "," in raw:
        parts = [p.strip() for p in raw.split(",")]
        last, first = parts[0], parts[-1]
        suffix = parts[1] if len(parts) == 3 else ""
        display = " ".join(x for x in (first, last, suffix) if x)
        last_tokens = [t for t in norm(last) if t not in SUFFIXES]
        first_tokens = norm(first)
    else:
        display = raw
        tokens = norm(raw)
        while tokens and tokens[-1] in SUFFIXES:
            tokens.pop()
        # Surname = last token, plus any particles before it ("de Robles", "Dela Cruz").
        k = len(tokens) - 1
        while k - 1 > 0 and tokens[k - 1] in PARTICLES:
            k -= 1
        last_tokens, first_tokens = tokens[k:], tokens[:k]
    initial = first_tokens[0][0] if first_tokens else ""
    return display, " ".join(last_tokens), initial


def name_key(display):
    _, surname, initial = split_bib_name(display)
    return (surname, initial)


def srg_keys():
    people = yaml.safe_load((ROOT / "data" / "people.yml").read_text(encoding="utf-8"))
    alumni = yaml.safe_load((ROOT / "data" / "alumni.yml").read_text(encoding="utf-8"))
    names = []
    for group in people:
        for m in group.get("members") or []:
            names.append(re.sub(r"\s*\(.*?\)\s*", " ", m["name"]).strip())
    for cohort in alumni["cohorts"]:
        names.extend(g["name"] for g in cohort["graduates"])
    return {name_key(n): n for n in names}


# ---------------------------------------------------------------------- venue
def venue(e):
    parts = []
    if e["type"] == "article":
        v = clean(e.get("journal", ""))
        vol = clean(e.get("volume", ""))
        if vol:
            v += f", {vol}"
            if e.get("number"):
                v += f"({clean(e['number'])})"
            if e.get("pages"):
                v += f":{clean(e['pages'])}"
        elif e.get("pages"):
            v += f", pp. {clean(e['pages'])}"
        parts.append(v)
    else:
        v = clean(e.get("booktitle", ""))
        if e.get("pages"):
            v += f", pp. {clean(e['pages'])}"
        parts.append(v)
    when = " ".join(x for x in (clean(e.get("month", "")), clean(e.get("year", ""))) if x)
    if when:
        parts.append(when)
    return ", ".join(p for p in parts if p)


def links(e):
    out = []
    if e.get("pdf"):
        out.append({"label": "PDF", "url": PDF_BASE + e["pdf"].strip()})
    if e.get("doi"):
        out.append({"label": "DOI", "url": "https://doi.org/" + e["doi"].strip()})
    for url, label in re.findall(r"\\href\{([^}]*)\}\{\[?([^\]}]*)\]?\}", e.get("note", "")):
        out.append({"label": " ".join(label.split()), "url": url})
    return out


# ----------------------------------------------------------------------- main
def main():
    src = sys.argv[1] if len(sys.argv) > 1 else BIB_URL
    entries = parse_bib(read_bib(src))
    keys = srg_keys()

    kept, dropped = [], []
    for e in entries:
        authors = []
        for raw in re.split(r"\s+and\s+", e.get("author", "")):
            if not raw.strip():
                continue
            display, surname, initial = split_bib_name(raw)
            authors.append({"name": display, "srg": (surname, initial) in keys})
        item = {
            "title": sentence_title(e.get("title", "")),
            "authors": authors,
            "venue": venue(e),
            "year": int(re.sub(r"\D", "", e.get("year", "0")) or 0),
            "links": links(e),
        }
        (kept if any(a["srg"] for a in authors) else dropped).append(item)

    kept.sort(key=lambda x: -x["year"])  # stable: keeps the .bib order within a year
    header = (
        f"# Full SRG publications list (shown on publications.html).\n"
        f"# Generated by tools/fetch_publications.py from {src}\n"
        f"# on {datetime.date.today().isoformat()}; kept: papers with at least one SRG faculty, student or alumni author\n"
        f"# (authors with srg: true are shown in bold). Safe to edit by hand; re-running the script overwrites it.\n"
    )
    OUT.write_text(
        header + yaml.safe_dump(kept, sort_keys=False, allow_unicode=True, width=10_000),
        encoding="utf-8",
    )
    print(f"{len(entries)} entries read; kept {len(kept)}, excluded {len(dropped)} -> {OUT.relative_to(ROOT)}")
    for d in dropped:
        print(f"  excluded: {d['year']}  {', '.join(a['name'] for a in d['authors'])} - {d['title']}")


if __name__ == "__main__":
    main()
