"""Pelican settings for publishing to https://srg-ics-uplb.github.io."""
import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *  # noqa: E402,F401,F403

SITEURL = "https://srg-ics-uplb.github.io"
RELATIVE_URLS = False

FEED_DOMAIN = SITEURL
FEED_ATOM = "feeds/news.atom.xml"

DELETE_OUTPUT_DIRECTORY = True
