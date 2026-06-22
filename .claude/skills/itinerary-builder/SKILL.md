---
name: itinerary-builder
description: Build a stylish one-page travel/event itinerary (旅程表・予定表) PDF from source documents (PDFs, images, emails). Use when the user asks to create or update an itinerary, schedule, or 旅程表/予定表 from convention invitations, flight/hotel confirmations, or screenshots — especially Lions Clubs international convention (国際大会) trips. Extracts flights, hotel, events, venues/addresses, and attendance choices, then renders a navy/gold themed single-page PDF (and HTML for cloud storage).
---

# Itinerary Builder (旅程表ビルダー)

Produce a clean, single-page itinerary that matches the user's "usual format":
a `日付 / 時間 / 予定` table with flights, key events, venue addresses, and a
hotel card, in a navy × gold Lions theme.

## Workflow

### 1. Read every source document
Source files are usually Japanese PDFs (event invitations) and phone
screenshots (flight/hotel confirmations).

- **Text PDFs**: extract with PyMuPDF.
  ```python
  import fitz
  for f in pdfs:
      doc = fitz.open(f)
      for p in doc: print(p.get_text())
  ```
- **Image-only PDFs / screenshots** (text extraction returns blank, page has
  images): render to PNG, then Read the PNG so the model can see it.
  ```python
  doc[0].get_pixmap(matrix=fitz.Matrix(2,2)).save("/tmp/page.png")
  ```
- If `pymupdf`/`fpdf2` import fails with `_cffi_backend` /
  `pyo3_runtime.PanicException`, the cryptography stack is broken — fix with:
  `pip3 install --force-reinstall cffi`. `poppler-utils` is usually NOT
  installable; use PyMuPDF instead of pdftotext/pdftoppm.

### 2. Extract and confirm the trip facts
Collect into the `DAYS` data structure (see `scripts/gen_itinerary_pdf.py`):
- **Convention**: name, dates, official venue.
- **Flights**: airline/flight no., route, dep/arr times (outbound + return).
- **Hotel**: name, full address, booking ref.
- **Events**: date, time, name, venue + **address** (and TEL when known).
- **Attendance**: which overlapping events the user attends/skips — ask the
  user if two events conflict; mark chosen ones as key (`True`).
- Mark dinners / ceremonies / honoree events as `key=True` (gold highlight).
- Leave undecided venues as "会場未定" rather than guessing.

Re-confirm anything ambiguous (e.g. a date that doesn't match a known event)
with the user before finalizing.

### 3. Generate the PDF (one page, stylish)
Use `scripts/gen_itinerary_pdf.py` as the template. Edit the `DAYS`, hotel,
header, and flight data at the top, then run it.
```bash
pip3 install --force-reinstall cffi   # only if imports are broken
pip3 install fpdf2 pymupdf
python3 scripts/gen_itinerary_pdf.py
```
Design notes:
- Font: `/usr/share/fonts/truetype/fonts-japanese-gothic.ttf` (IPAGothic).
  IPAGothic LACKS emoji (✅❌✈ render as tofu) — use text/○/★/● and color
  instead. `●` `★` `○` are safe.
- Palette: navy `#172a4d`, navy2 `#264073`, gold `#c0983e`, blue `#2962a8`.
- Layout: navy header banner + gold rule; `日付/時間/予定` table with merged
  navy date cells, alternating row backgrounds, gold accent bar + bold navy
  text for key events, grey sub-line for addresses; rounded hotel card.
- Always verify by rendering the output PDF to PNG and Reading it; check it's
  **one page** and nothing overflows/overlaps.

### 4. Verify visually
```python
import fitz
doc = fitz.open(out_pdf)
print("pages", len(doc))         # must be 1
doc[0].get_pixmap(matrix=fitz.Matrix(2,2)).save("/tmp/check.png")
```
Then Read `/tmp/check.png`.

### 5. Deliver
- `SendUserFile` the PDF to the user.
- Commit the PDF + generator script to the working branch and push.

### 6. Optional: save to cloud storage (Box / Google Drive)
- **Box MCP `upload_file` only accepts TEXT** (txt/md/html/svg/csv/json…),
  **not binary PDF**. To put the itinerary in a Box folder, generate the HTML
  version (`scripts/gen_itinerary_html.py`) and upload that — Box previews and
  prints it. Find the folder with `search_folders_by_name`; uploads may need
  the user to approve the write permission.
- **Google Drive MCP `create_file` CAN take binary** via `base64Content` +
  `contentMimeType: application/pdf` — use this if the actual PDF must live in
  Drive.
- Don't overwrite an existing file blindly; a Box upload with a duplicate name
  errors. Use a clear, distinct file name.

## Files
- `scripts/gen_itinerary_pdf.py` — themed one-page PDF generator (edit `DAYS`).
- `scripts/gen_itinerary_html.py` — matching HTML for Box/cloud or printing.

Both scripts are self-contained templates: update the data block at the top
for a new trip and re-run.
