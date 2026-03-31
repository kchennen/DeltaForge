<!-- markdownlint-disable MD013 MD033 MD041 -->
<div align="center">

<h1>DeltaForge</h1>

<p><em>Compare anything, instantly — text, spreadsheets, PDFs, and images.</em></p>

## Project Information

[![License](https://img.shields.io/github/license/kchennen/DeltaForge?style=flat-square&logo=opensourceinitiative)](LICENSE) [![Python](https://img.shields.io/badge/python->=3.13-blue?style=flat-square&logo=python)](https://www.python.org/)

## We rely on

[![Dash](https://img.shields.io/badge/Dash-latest?style=flat-square&logo=plotly&color=3F4F75)](https://dash.plotly.com/) [![Mantine](https://img.shields.io/badge/Mantine-latest?style=flat-square&logo=mantine&color=339AF0)](https://www.dash-mantine-components.com/) [![PyMuPDF](https://img.shields.io/badge/PyMuPDF-latest?style=flat-square&logo=python&color=E74C3C)](https://pymupdf.readthedocs.io/) [![Pillow](https://img.shields.io/badge/Pillow-latest?style=flat-square&logo=python&color=8B5CF6)](https://pillow.readthedocs.io/) [![Pandas](https://img.shields.io/badge/Pandas-latest?style=flat-square&logo=pandas&color=150458)](https://pandas.pydata.org/)

## Quality

[![CI](https://img.shields.io/github/actions/workflow/status/kchennen/DeltaForge/ci.yml?label=ci&style=flat-square&logo=github-actions)](https://github.com/kchennen/DeltaForge/actions/workflows/ci.yml) [![Mypy](https://img.shields.io/badge/mypy-checked-informational?style=flat-square&logo=python)](https://mypy-lang.org/) [![Ruff](https://img.shields.io/badge/code%20style-ruff-000000?style=flat-square&logo=python)](https://github.com/astral-sh/ruff) [![GitHub issues](https://img.shields.io/github/issues/kchennen/DeltaForge?style=flat-square&logo=github)](https://github.com/kchennen/DeltaForge/issues) [![Report a bug](https://img.shields.io/badge/🐛%20Report%20a%20bug-red?style=flat-square)](https://github.com/kchennen/DeltaForge/issues)
</div>
<!-- markdownlint-enable MD013 MD033 MD041 -->

---

DeltaForge is an open-source, browser-based diff toolkit
for comparing files side by side. It runs entirely in your
browser — nothing leaves your machine. Built with Dash and
Mantine, it provides a clean, responsive UI with light and
dark themes.

---

## Features

- 📝 **Text Diff** — compare two text blocks with line, word, or character-level granularity
- 📊 **Excel Diff** — compare spreadsheets cell by cell; detect added, removed, and modified cells
- 📄 **PDF Diff** — compare PDF documents page by page — text extraction, visual overlay, and redline
- 🏞️ **Image Diff** — find pixel-level differences between images with five comparison modes
- 🔢 **Duplicate Counter** — find and count duplicate values in a list; export unique values with occurrence counts
- 🔒 **Private by design** — all comparisons run locally in your browser
- 🎨 **Light & dark themes** — seamless toggle in the header
- 🚀 **No sign-up required** — open source and free

---

## Installation

```bash
# Clone the repository
git clone https://github.com/kchennen/DeltaForge.git
cd DeltaForge

# Using uv (recommended)
uv sync

# Using pip
pip install -e .
```

---

## Quick Start

```bash
# Run the development server
python -m app.web.main

# Or with gunicorn for production
gunicorn app.web.main:server -b 0.0.0.0:8050
```

Then open [http://localhost:8050](http://localhost:8050) in your browser.

---

## Development

```bash
uv sync --all-groups        # install all dependencies

uv run pytest               # run tests
uv run mypy app/            # type check
uv run ruff check app/      # lint
uv run ruff format app/     # format
```

### Project structure

```text
app/
├── web/
│   ├── pages/         # Dash pages (home, text, excel, pdf, image, duplicates)
│   ├── layouts/       # Main layout and shared components
│   ├── callbacks/     # Dash callbacks per tool
│   ├── components/    # Reusable UI components
│   ├── assets/        # CSS, JS, fonts, images
│   └── app.py         # Dash app factory
├── core/              # Core diff logic (text, excel, pdf, image)
└── tests/
```

---

## Roadmap

- [x] Text diff (line / word / char)
- [x] Excel diff (cell-level)
- [x] PDF diff (text / visual / redline)
- [x] Image diff (5 view modes)
- [x] Duplicate counter
- [x] Light & dark themes
- [x] CI pipeline
- [ ] CSV diff
- [ ] JSON / YAML diff
- [ ] Folder diff
- [ ] Drag & drop file upload
- [ ] Shareable diff links

---

Built with ❤️ for your pleasure and our leisure by the 🦡 **Blaireau Company**
