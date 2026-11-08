"""One-off migration: scrape the hand-written HTML site into data/*.yml and content/news/*.md.

Usage:  .venv/bin/python tools/extract.py /path/to/old/site/checkout

After the migration, the YAML/Markdown files are the source of truth; this script is kept
only as a record of how they were produced.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, Comment, NavigableString

SRC = Path(sys.argv[1])
DATA = Path("data")
NEWS = Path("content/news")


def soup(name):
    return BeautifulSoup((SRC / name).read_text(encoding="utf-8"), "html.parser")


def text(el):
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""


def inner(el):
    """Inner HTML with whitespace collapsed."""
    if el is None:
        return ""
    html = "".join(str(c) for c in el.contents)
    return " ".join(html.split())


def link_info(el):
    """href/new_tab for an <a> card; None href for a non-link <div> card."""
    if el.name != "a":
        return {}
    info = {"href": el.get("href", "").strip('"')}
    if el.get("target") == "_blank":
        info["new_tab"] = True
    return info


class Dumper(yaml.SafeDumper):
    pass


def _str(dumper, s):
    style = "|" if "\n" in s else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", s, style=style)


Dumper.add_representer(str, _str)


def dump(name, obj):
    path = DATA / name
    path.write_text(
        yaml.dump(obj, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=10_000),
        encoding="utf-8",
    )
    print("wrote", path)


# ---------------------------------------------------------------- home page
idx = soup("index.html")
header = idx.select_one("header.header")
about = idx.select_one("#about")
site = {
    "tagline": text(header.find("p")),
    "about": [inner(p) for p in about.find_all("p")],
}

people = []
for h3 in idx.select("#people > h3"):
    grid = h3.find_next_sibling("div", class_="people-grid")
    members = []
    for card in grid.find_all(class_="person-card", recursive=False):
        m = {"name": text(card.find("h3"))}
        m.update(link_info(card))
        img = card.find("img")
        if img:
            m["photo"] = img["src"]
        for p in card.find_all("p", recursive=False):
            if p.find("strong"):
                m["title"] = text(p)
            else:
                m["interests"] = text(p)
        members.append(m)
    people.append({"group": text(h3), "members": members})

research = idx.select_one("#research")
research_data = {
    "intro": inner(research.find("p", recursive=False)),
    "areas": [
        {"title": text(c.find("h3")), "text": inner(c.find("p"))}
        for c in research.select(".research-card")
    ],
}

pubs = idx.select_one("#publications")
publications = {
    "items": [
        {
            "title": text(p.select_one(".publication-title")),
            "authors": text(p.select_one(".publication-authors")),
            "venue": text(p.select_one(".publication-venue")),
        }
        for p in pubs.select(".publication-item")
    ],
    "all_url": pubs.select("a.resource-link")[-1]["href"],
}

courses = []
for c in idx.select("#courses .course-card"):
    d = {
        "code": " ".join(text(c.select_one(".course-code")).split()),
        "title": text(c.find("h3")),
        "description": text(c.find("p")),
    }
    d.update(link_info(c))
    courses.append(d)


def cards(section):
    out = []
    for c in section.select(".resource-link"):
        d = {"title": text(c.find("h4")), "description": inner(c.find("p"))}
        d.update(link_info(c))
        out.append(d)
    return out


join = idx.select_one("#join")
join_data = {"intro": inner(join.find("p", recursive=False)), "cards": cards(join)}
resources = cards(idx.select_one("#resources"))

dump("site.yml", site)
dump("people.yml", people)
dump("research.yml", research_data)
dump("publications.yml", publications)
dump("courses.yml", courses)
dump("join.yml", join_data)
dump("resources.yml", resources)

# ---------------------------------------------------------------- seminars
sem = soup("seminars.html")
seminars = []
for item in sem.select(".seminar-item"):
    when = text(item.select_one(".seminar-datetime"))
    parts = [p.strip() for p in when.split("|")]
    date_s = re.sub(r"^\W+", "", parts[0]).strip()
    date = datetime.strptime(" ".join(date_s.split()), "%B %d, %Y").date()
    poster = item.select_one(".poster-link").get("href", "")
    inners = item.select(".collapsible-inner p")
    seminars.append(
        {
            "id": item["id"],
            "title": text(item.find("h3")),
            "speaker": inner(item.select_one(".seminar-speaker")),
            "affiliation": text(item.select_one(".seminar-affiliation")),
            "date": date.isoformat(),
            "time": re.sub(r"^\W+", "", parts[1]).strip(),
            "venue": re.sub(r"^\W+", "", parts[2]).strip(),
            "poster": poster,
            "abstract": inner(inners[0]),
            "bio": inner(inners[1]),
        }
    )
dump("seminars.yml", seminars)

# ---------------------------------------------------------------- alumni
alu = soup("alumni.html")
cohorts = []
for co in alu.select(".cohort"):
    grads = []
    for li in co.select("li"):
        name_el = li.select_one(".name")
        g = {"name": text(name_el)}
        a = name_el.find("a")
        if a:
            g["link"] = a["href"]
        honors = [text(s) for s in li.select(".honor")]
        if honors:
            g["honors"] = honors
        for key in ("role", "adviser"):
            el = li.select_one("." + key)
            if el:
                g[key] = text(el)
        grads.append(g)
    cohorts.append({"cohort": text(co.find("h2")), "graduates": grads})
dump(
    "alumni.yml",
    {"intro": inner(alu.select_one("p.intro")), "cohorts": cohorts},
)

# ---------------------------------------------------------------- news
news = soup("news.html")
section = news.select_one("section.section")
# Items that are live on the page, plus the commented-out ones (kept as drafts).
blocks = [(el, "published") for el in section.select("div.news-content")]
for c in section.find_all(string=lambda s: isinstance(s, Comment)):
    for el in BeautifulSoup(str(c), "html.parser").select("div.news-content"):
        blocks.append((el, "draft"))

NEWS.mkdir(parents=True, exist_ok=True)
for el, status in blocks:
    wrapper = el.parent
    slug = wrapper["id"]
    date = datetime.strptime(text(el.select_one(".news-date")), "%B %d, %Y").date()
    meta = {
        "Title": text(el.select_one(".news-title")),
        "Date": date.isoformat(),
        "Slug": slug,
    }
    if "featured-news" in (wrapper.get("class") or []):
        meta["Featured"] = "true"
    holder = el.select_one(".news-placeholder")
    img = holder.find("img") if holder else None
    if img:
        meta["Image"] = img["src"].lstrip("./")
        meta["Image_alt"] = img.get("alt", "")
    elif holder:
        meta["Icon"] = text(holder)
    label = el.select(".news-meta span")
    if label:
        meta["Label"] = text(label[-1])
    if status == "draft":
        meta["Status"] = "draft"
    desc = el.select_one(".news-description")
    body = "\n".join(line.strip() for line in "".join(str(c) for c in desc.contents).strip().splitlines())
    header_lines = "\n".join(f"{k}: {v}" for k, v in meta.items())
    path = NEWS / f"{date.isoformat()}-{slug}.md"
    path.write_text(f"{header_lines}\n\n{body}\n", encoding="utf-8")
    print("wrote", path, f"({status})")
