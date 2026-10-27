# StateShift Manuscript Source & Publication Companion

**Manuscript Title**: *StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training*  
**Author**: Sham Satish Thakare (Independent Researcher, Pune, Maharashtra, India)  
**Publication Status**: Submitted to *Artificial Intelligence* (Elsevier), 2026 — Manuscript ARTINT-D-26-01491  

---

## Directory Overview

This directory contains the public LaTeX source files and publication companion assets for the StateShift manuscript:

* `main.tex`: Full manuscript LaTeX source file.
* `supplement.tex`: Supplementary Material LaTeX source file.
* `references.bib`: BibTeX bibliography file (8 verified items).

---

## Compilation Instructions

To compile the PDF using `pdflatex` or `latexmk`:

```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```
