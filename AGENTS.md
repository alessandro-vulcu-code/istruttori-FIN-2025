# AGENTS.md - Guidelines for AI Coding Agents

This repository contains course materials for the FIN (Federazione Italiana Nuoto) swimming instructor certification course.

## Repository Structure

- `Lezioni/` - Markdown lesson summaries (28 lessons numbered 1-28)
- `Trascrizioni/` - Raw transcription files from FAD platform
- `Corso istruttori FIN 2025.tex` - LaTeX master document
- `Corso istruttori FIN 2025.pdf` - Generated PDF output
- `fix_tables.py` - Python helper script for LaTeX table formatting
- `PROMPT.md` - Guidelines for processing transcriptions

## Build Commands

### Generate PDF from LaTeX
```bash
# Compile with LuaLaTeX (recommended for OpenType fonts)
lualatex "Corso istruttori FIN 2025.tex"

# Or compile with XeLaTeX
xelatex "Corso istruttori FIN 2025.tex"

# Full compilation with bibliography (if needed)
lualatex "Corso istruttori FIN 2025.tex" && lualatex "Corso istruttori FIN 2025.tex"
```

### Fix LaTeX Table Overflows
```bash
python3 fix_tables.py
```

This fixes Overfull \hbox warnings by converting fixed-width columns to proportional `p{}` columns.

### Convert Markdown to LaTeX (via Pandoc)
```bash
# Convert single lesson to LaTeX
pandoc -f markdown -t latex "Lezioni/1. Aspetti Amministrativi.md" -o output.tex

# Convert with custom template
pandoc -f markdown -t latex --template=template.tex "input.md" -o output.tex
```

## Document Processing Workflow

When processing transcriptions to create lesson summaries:

1. Read the transcription from `Trascrizioni/`
2. Create structured summary in `Lezioni/` following the guidelines in `PROMPT.md`
3. Export to LaTeX and compile PDF

## Content Guidelines

### Language and Formatting
- **Language**: Italian only
- **Encoding**: UTF-8 with proper accented characters (à, è, é, ì, ò, ù)
- **No emojis**: Strictly prohibited
- **Tone**: Professional, natural, human-like (not overly verbose)

### Markdown Structure
```markdown
# [Lesson Number]. [Title]

## Introduzione
Brief overview of the lesson topic.

## [Section Title]
### [Subsection]
Content with **bold keywords** and *italic definitions*.

- Bullet points for technical steps
- Tables for comparisons

## Conclusione
Key takeaways for exam preparation.
```

### Naming Conventions
- Lesson files: `[Number].[Topic].md` (e.g., `1. Aspetti Amministrativi.md`)
- Transcriptions: `[Number].TRASCRIZIONE_[Topic] Piattaforma FAD FIN.txt`
- Use sentence case for titles
- Number lessons sequentially from 1-28

### Typography
- Use `**bold**` for key terms and important concepts
- Use `*italic*` for definitions and foreign terms
- Technical terms in English should be preserved (e.g., *backstroke*, *butterfly*)
- Tables for comparing data, styles, or concepts
- Bullet points for sequential technical instructions

### LaTeX Guidelines
- Use `longtable` environment for multi-page tables
- Fix Overfull \hbox warnings using `fix_tables.py`
- Replace `\captionsetup[table]` with `\captionsetup[longtable]`
- Use proportional column specs: `p{0.47\linewidth}` instead of `ll`

## Code Style (Python)

When editing `fix_tables.py` or creating new scripts:

- Python 3.6+ compatible
- Use `#!/usr/bin/env python3` shebang
- UTF-8 encoding explicitly: `encoding='utf-8'`
- Document purpose in docstring
- Print informative status messages

## Error Handling

- Preserve all technical details from source material
- Do not skip fundamental concepts
- Do not invent citations or external references
- Flag unclear content rather than guessing

## File Operations

- Always verify file paths with spaces are properly quoted
- Read existing files before modifying
- Maintain UTF-8 encoding throughout
- Keep backup of original LaTeX before running fix_tables.py

## Testing

There are no automated tests in this repository. Changes should be verified by:
1. Compiling LaTeX successfully (no errors/warnings)
2. Reviewing generated PDF formatting
3. Checking Markdown renders correctly in Obsidian
