"""Pelican settings for the Systems Research Group site (local development).

Content lives in two places:
  * content/news/*.md  - news items (one Markdown file each; `Status: draft` hides one)
  * data/*.yml         - people, courses, publications, seminars, alumni, etc.
"""
import datetime
from pathlib import Path

import yaml

AUTHOR = "Systems Research Group"
SITENAME = "Systems Research Group @ UPLB ICS"
SITEURL = ""
# Absolute address of the live site, used for canonical/Open Graph tags.
SITE_ABS_URL = "https://srg-ics-uplb.github.io"
CONTACT_EMAIL = "jchermocilla@up.edu.ph"
CURRENT_YEAR = datetime.date.today().year

PATH = "content"
THEME = "theme/srg"
TIMEZONE = "Asia/Manila"
DEFAULT_LANG = "en"
DEFAULT_DATE_FORMAT = "%B %-d, %Y"
RELATIVE_URLS = True

# --- Data files ------------------------------------------------------------
_DATA_DIR = Path(__file__).parent / "data"
SRG = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(_DATA_DIR.glob("*.yml"))}

# --- Main menu (rendered on every page by theme/srg/templates/_macros.html) --
# `section` links point at an anchor on the home page; `page` links are site pages.
SRG_MENU = [
    ("Home", "home"),
    ("Research", "#research"),
    ("People", "#people"),
    ("Publications", "#publications"),
    ("Courses", "#courses"),
    ("Seminars", "seminars.html"),
    ("News", "news.html"),
    ("Join Us", "#join"),
    ("Resources", "#resources"),
    ("Blog", "https://srg-ics-uplb.github.io/blog/"),
]

# --- Content ---------------------------------------------------------------
ARTICLE_PATHS = ["news"]
PAGE_PATHS = ["pages"]
READERS = {"html": None}  # .html files under content/ are copied as-is, not parsed

STATIC_PATHS = [
    "images",
    "logos",
    "seminars",
    "cs-specialization.html",
    "extra/robots.txt",
]
EXTRA_PATH_METADATA = {"extra/robots.txt": {"path": "robots.txt"}}

# --- Output URLs: keep the old site's addresses -----------------------------
ARTICLE_URL = "news/{slug}.html"
ARTICLE_SAVE_AS = "news/{slug}.html"
PAGE_URL = "{slug}.html"
PAGE_SAVE_AS = "{slug}.html"
DRAFT_SAVE_AS = ""
DRAFT_PAGE_SAVE_AS = ""

DIRECT_TEMPLATES = ["index", "news", "seminars", "alumni", "404", "sitemap"]
INDEX_SAVE_AS = "index.html"
NEWS_SAVE_AS = "news.html"
SEMINARS_SAVE_AS = "seminars.html"
ALUMNI_SAVE_AS = "alumni.html"
PAGINATED_TEMPLATES = {}
DEFAULT_PAGINATION = False

AUTHOR_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
TAG_SAVE_AS = ""
TAGS_SAVE_AS = ""
ARCHIVES_SAVE_AS = ""

# Feeds are generated only for the published site (publishconf.py).
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# --- Sitemap ---------------------------------------------------------------
# theme/srg/templates/sitemap.xml lists these plus every published news item.
SITEMAP_SAVE_AS = "sitemap.xml"
SITEMAP_PAGES = [
    "",
    "news.html",
    "seminars.html",
    "alumni.html",
    "collab.html",
    "cs-specialization.html",
    "seminars/2026/01_cyber_xai.html",
]
BUILD_DATE = datetime.date.today().isoformat()


# --- Template helpers ------------------------------------------------------
def _longdate(value):
    """'2026-05-05' (or a date) -> 'May 5, 2026'."""
    if isinstance(value, str):
        value = datetime.date.fromisoformat(value)
    return f"{value:%B} {value.day}, {value.year}"


JINJA_FILTERS = {"longdate": _longdate}
