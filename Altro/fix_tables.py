#!/usr/bin/env python3
"""
Fix longtable column specs to prevent Overfull \hbox.
Replaces fixed 'l' column specs with 'p{}' proportional columns.
"""
import re

INPUT_FILE = "Corso istruttori FIN 2025.tex"
OUTPUT_FILE = "Corso istruttori FIN 2025.tex"

# Map: number of 'l' columns -> proportional p{} spec
# Total usable width = \linewidth, minus column separators (approx 2*\tabcolsep per col)
# We use slightly less than equal parts to leave breathing room
COL_SPECS = {
    # @{} removes outer padding; p{} columns wrap text automatically
    # 2 cols: each gets ~0.47\linewidth
    r'\begin{longtable}[]{@{}ll@{}}':
        r'\begin{longtable}[]{@{}p{0.47\linewidth}p{0.47\linewidth}@{}}',

    # 3 cols: each gets ~0.30\linewidth
    r'\begin{longtable}[]{@{}lll@{}}':
        r'\begin{longtable}[]{@{}p{0.30\linewidth}p{0.30\linewidth}p{0.30\linewidth}@{}}',

    # 4 cols: each gets ~0.22\linewidth
    r'\begin{longtable}[]{@{}llll@{}}':
        r'\begin{longtable}[]{@{}p{0.22\linewidth}p{0.22\linewidth}p{0.22\linewidth}p{0.22\linewidth}@{}}',
}

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

total_replacements = 0
for old, new in COL_SPECS.items():
    count = content.count(old)
    content = content.replace(old, new)
    print(f"  Replaced {count}x: {old[:50]}...")
    total_replacements += count

# Also fix the \captionsetup[table] warning:
# The warning says it's unused because longtable uses its own caption system.
# We should remove or replace \captionsetup[table] with \captionsetup[longtable]
old_caption = r'\captionsetup[table]{skip=10pt} % Spazio tra didascalia e tabella'
new_caption = r'\captionsetup[longtable]{skip=10pt} % Spazio tra didascalia e longtable'
if old_caption in content:
    content = content.replace(old_caption, new_caption)
    print(f"  Fixed captionsetup[table] -> captionsetup[longtable]")
    total_replacements += 1

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone! Total replacements: {total_replacements}")
print(f"Saved to: {OUTPUT_FILE}")
