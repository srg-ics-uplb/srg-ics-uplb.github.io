# Systems Research Group website

Source for https://srg-ics-uplb.github.io, built with [Pelican](https://getpelican.com).

## Editing content

| To change… | Edit |
|---|---|
| Faculty, and the Graduate/Undergraduate Students name lists (People) | `data/people.yml` |
| Home page tagline and About text | `data/site.yml` |
| Research areas (and their collaborators: people or institutions) | `data/research.yml` |
| Selected publications (home page) | `data/publications.yml` |
| Full publications list (publications.html) | `data/publications_all.yml`, refresh with `.venv/bin/python tools/fetch_publications.py` |
| Courses | `data/courses.yml` |
| Join Us section | `data/join.yml` |
| Resources section | `data/resources.yml` |
| Seminars and talks | `data/seminars.yml` (shown newest first, sorted by `date`) |
| Alumni | `data/alumni.yml` |
| News | add a file to `content/news/` (see below) |
| Collaboration page | `content/pages/collab.md` |
| Main menu | `SRG_MENU` in `pelicanconf.py` |

Images go in `content/images/`, and are referenced as `images/...`. Files under
`content/seminars/` and `content/cs-specialization.html` are copied as they are.

### Adding a news item

Create `content/news/YYYY-MM-DD-short-name.md`:

```markdown
Title: Congratulations 2026 graduates!
Date: 2026-07-20
Slug: graduating-class-2026
Featured: true
Image: images/news/003-class2026.webp
Image_alt: SRG class of 2026

Text of the news item, in Markdown.
```

`Featured: true` gives the dark highlighted card. Use `Icon: 🎓` instead of `Image` for an emoji tile,
and `Status: draft` to keep an item out of the site.

## Building locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pelican content -s pelicanconf.py --listen --autoreload   # http://localhost:8000
```

## Publishing

`.github/workflows/pelican.yml` builds with `publishconf.py` and deploys to GitHub Pages on every push to
`master`, once the repository's Pages source is set to **GitHub Actions**.

## Layout

- `theme/srg/templates/`: page templates. `base.html` is the shared `<head>`; `_macros.html` holds the
  menu, header, footer and card helpers.
- `theme/srg/static/css/`, `theme/srg/static/js/`: per-page styles and scripts (carried over unchanged from the
  hand-written site).
- `tools/extract.py`: the one-off script that migrated the old HTML into `data/` and `content/news/`.
