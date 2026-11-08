"""Pelican settings for the mirror at https://research.ics.uplb.edu.ph/labs/srg/home (Docker image).

GitHub Pages (https://srg-ics-uplb.github.io) stays the primary address: canonical, Open Graph
and sitemap URLs still point there (SITE_ABS_URL), so search engines treat this copy as a mirror.

All links are relative, so the build works under any path prefix. Only the 404 page, which the
server returns at arbitrary depths, needs the prefix itself: set it with SRG_BASE_PATH.
"""
import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *  # noqa: E402,F401,F403

SITEURL = ""
RELATIVE_URLS = True
SITE_ROOT_PATH = os.environ.get("SRG_BASE_PATH", "/labs/srg/home").rstrip("/")

FEED_ATOM = None  # the news feed is published on the primary site only

DELETE_OUTPUT_DIRECTORY = True
