import re

INPUT = 'Domande.md'
OUTPUT = 'Domande.md'  # sovrascrive in-place; cambia se vuoi un file separato

with open(INPUT, 'r') as f:
    content = f.read()

# Converte "[ A ] testo" -> "- [ ] A. testo"
content = re.sub(r'\[ ([A-D]) \] ', r'- [ ] \1. ', content)

with open(OUTPUT, 'w') as f:
    f.write(content)

print("Conversione completata.")
