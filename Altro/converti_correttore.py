"""
Converte il PDF del correttore in Markdown.
- pdftoppm rasterizza ogni pagina a 400dpi
- Ritaglia le due colonne di lettere e OCR l'intera striscia con tesseract
- Associa le lettere ai numeri di domanda in base alla posizione nella pagina
"""

import re, subprocess, os
import numpy as np
from PIL import Image

PDF_PATH = '2024_11_16 Correttore.pdf'
OUTPUT   = 'Correttore.md'
TMP_DIR  = '/tmp/correttore_pages'
DPI      = 400
PT_TO_PX = DPI / 72.0

# Coordinate colonne lettere (punti PDF → pixel)
# Ricavate dal debug visivo + layout pdfminer
LEFT_X0  = int(183 * PT_TO_PX)
LEFT_X1  = int(220 * PT_TO_PX)
RIGHT_X0 = int(476 * PT_TO_PX)
RIGHT_X1 = int(512 * PT_TO_PX)
# Zona verticale della tabella (pt dal basso → px dall'alto su A4=841pt)
PAGE_H_PT = 841
TABLE_TOP_PT    = 745   # sopra la prima riga
TABLE_BOTTOM_PT = 110   # sotto l'ultima riga
TABLE_Y0 = int((PAGE_H_PT - TABLE_TOP_PT) * PT_TO_PX)
TABLE_Y1 = int((PAGE_H_PT - TABLE_BOTTOM_PT) * PT_TO_PX)

os.makedirs(TMP_DIR, exist_ok=True)

# ── 1. Rasterizza tutte le pagine ──────────────────────────────────────────
print("Rasterizzazione pagine PDF…")
subprocess.run(
    ['pdftoppm', '-r', str(DPI), '-png', PDF_PATH, f'{TMP_DIR}/page'],
    check=True
)
page_files = sorted(f for f in os.listdir(TMP_DIR) if f.endswith('.png'))
num_pages  = len(page_files)
print(f"  {num_pages} pagine trovate.")

# Spaziatura righe (ricavata empiricamente dalle coordinate pdfminer pagina 1)
ROW_Y_START = 666    # y_px del centro riga 0 (Q1, Q51, …)
ROW_Y_STEP  = 139    # pixel tra una riga e la successiva

# ── 2. OCR di una colonna intera ───────────────────────────────────────────
def ocr_column(img, x0, x1):
    """OCR di una striscia verticale, restituisce lista di lettere."""
    strip = img.crop((x0, TABLE_Y0, x1, TABLE_Y1))
    strip = strip.resize((strip.width * 4, strip.height * 4), Image.LANCZOS)
    strip.save('/tmp/_strip.png')
    r = subprocess.run(
        ['tesseract', '/tmp/_strip.png', 'stdout',
         '--psm', '6', '-c', 'tessedit_char_whitelist=ABCD\n'],
        capture_output=True, text=True
    )
    return r.stdout.strip().split()

DARK_PIXEL_THRESHOLD = 1000  # sotto questa soglia la cella è vuota

def find_blank_rows(img, x0, x1):
    """Restituisce l'insieme degli indici di riga (0-24) con cella vuota."""
    arr = np.array(img.convert('L'))
    blank = set()
    for i in range(25):
        y0 = ROW_Y_START + i * ROW_Y_STEP - 120
        y1 = ROW_Y_START + i * ROW_Y_STEP + 20
        dark = int(np.sum(arr[y0:y1, x0:x1] < 128))
        if dark < DARK_PIXEL_THRESHOLD:
            blank.add(i)
    return blank

def ocr_column_robust(img, x0, x1):
    """OCR della colonna intera; se restituisce meno di 25 lettere,
    individua le righe vuote tramite conteggio pixel e reinserisce ''."""
    letters = ocr_column(img, x0, x1)
    if len(letters) == 25:
        return letters
    # Individua le righe vuote
    blank_rows = find_blank_rows(img, x0, x1)
    if not blank_rows:
        return letters  # non riusciamo a capire dove manca: lasciamo così
    # Ricostruisce la lista da 25 inserendo '' alle righe vuote
    result = []
    letter_iter = iter(letters)
    for i in range(25):
        if i in blank_rows:
            result.append('')
        else:
            result.append(next(letter_iter, '?'))
    return result

# ── 3. Processa ogni pagina ────────────────────────────────────────────────
answers = {}

for page_idx, page_file in enumerate(page_files):
    img    = Image.open(os.path.join(TMP_DIR, page_file))
    base_q = page_idx * 50  # prima domanda della pagina (0-based)

    left_letters  = ocr_column_robust(img, LEFT_X0, LEFT_X1)
    right_letters = ocr_column_robust(img, RIGHT_X0, RIGHT_X1)

    # Associa lettera → numero domanda (celle vuote vengono saltate)
    for i, letter in enumerate(left_letters):
        q = base_q + i + 1
        if letter:
            answers[q] = letter

    for i, letter in enumerate(right_letters):
        q = base_q + 25 + i + 1
        if letter:
            answers[q] = letter

    # Riepilogo pagina
    all_letters = [l for l in left_letters + right_letters if l]
    n_ok    = sum(1 for l in all_letters if l in 'ABCD')
    n_blank = 50 - len(all_letters)
    sample  = [(base_q + 1, left_letters[0] if left_letters else '?'),
               (base_q + 2, left_letters[1] if len(left_letters) > 1 else '?')]
    blank_note = f', {n_blank} vuote' if n_blank else ''
    print(f"Pag {page_idx+1:2d}: {n_ok} ok{blank_note} | "
          + ' '.join(f'Q{q}={l}' for q, l in sample))

# ── 4. Verifica ────────────────────────────────────────────────────────────
total   = len(answers)
missing = [n for n in range(1, 1001) if n not in answers]
bad     = [(n, l) for n, l in sorted(answers.items()) if l not in 'ABCD']

print(f"\nTotale risposte: {total}")
if missing: print(f"ATTENZIONE mancanti: {missing}")
if bad:     print(f"ATTENZIONE OCR incerto ({len(bad)}): {bad[:20]}")

# ── 5. Output Markdown ────────────────────────────────────────────────────
lines = [
    '# Correttore',
    '',
    f'Totale risposte: {total}',
    '',
    '| Domanda | Risposta |',
    '|--------:|:--------:|',
]
for num in range(1, 1001):
    letter = answers.get(num, '?')
    lines.append(f'| {num} | **{letter}** |')

with open(OUTPUT, 'w') as f:
    f.write('\n'.join(lines) + '\n')

print(f"Scritto '{OUTPUT}'.")
