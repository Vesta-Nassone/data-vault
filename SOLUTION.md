# Solution Notes

## Stack Choices

**Django + DRF** was the required stack. My default go-to is FastAPI, which I'm more comfortable with, but Django was the right call here - its batteries-included approach (auth, admin, ORM, migrations) eliminates a lot of boilerplate that FastAPI would require you to wire up manually. Within that constraint:

- **DRF** handles serialization, authentication, pagination, and filtering cleanly with minimal boilerplate. `TokenAuthentication` covers API clients; `SessionAuthentication` lets the HTMX UI reuse Django's login session — no duplication.
- **HTMX** is a natural fit for Django templates. Partial rendering via `hx-get/hx-post/hx-target/hx-swap` gives dynamic inline editing without a separate frontend build step or a JS framework. The field correction workflow (click Edit → swap row with input form → submit → swap back with updated row) maps directly onto HTMX's swap model.
- **Pico CSS** via CDN provides instant clean styling with zero configuration - appropriate given the limited time.

---

## Data Model Design

**UUID primary keys** on both `Document` and `Field` avoid exposing sequential IDs in URLs and are safe to generate client-side if needed.

**`form_type` as a free string** (not a FK to a FormType table) keeps the model flexible — new form types can be ingested without schema changes. In production, a controlled vocabulary table with validation would be ideal.

**`original_value` is immutable.** Corrections are stored in a separate `corrected_value` column alongside `corrected_at` and `corrected_by`. The `effective_value` property surfaces the correct value (COALESCE pattern) without destroying the audit trail. This means you always know what the machine extracted vs. what a human decided.

**`status` as a TextChoices enum** keeps the valid states explicit while remaining readable in the DB. The `processing` status exists so that long-running extraction (e.g., with Celery) can be tracked - even though extraction is currently synchronous.

---

## PDF Extraction

PyMuPDF (`fitz`) extracts raw text page-by-page. Field parsing uses regex heuristics against a dictionary of named patterns (customer_name, account_number, routing_number, amount, date, SSN, EIN, address, email).

**Fixed confidence of 0.70** is assigned to all regex matches. This is a limitation - regex either matches or it doesn't; there's no probabilistic signal.

---

## Search Implementation

`django-filter` drives the API list endpoint. The `DocumentFilter` handles:

- Exact `form_type` match
- Date range on `uploaded_at`
- Field key/value filtering via `__icontains` through the reverse FK (with `.distinct()` to prevent duplicates from the JOIN)

**Amount range filtering** casts `original_value` to a float via `Cast(..., FloatField())`. This works for well-formatted numeric strings but would fail silently on malformed data. In production, a dedicated `numeric_value` FloatField (populated at ingest time for numeric fields) would be more robust and index-friendly.

The HTMX search page uses `hx-trigger="keyup changed delay:300ms"` to debounce live queries, keeping the UX snappy without hammering the server.

---

## What I'd Do Differently With More Time

1. **Background processing with Celery + Redis.** PDF extraction is currently synchronous — the upload request blocks until extraction completes. For large or complex PDFs this is unacceptable. The `processing` status is already wired for this: a Celery task would pick up the document after the HTTP response is returned.

2. **Full correction audit log.** Currently only the last correction is tracked per field. A `FieldCorrection` event table (field FK, old value, new value, corrected_by, corrected_at) would give a full history and support reversions.

3. **S3 / object storage.** PDFs are currently saved to a local `media/` directory. In production, files should go to S3,GCS (or equivalent) with `django-storages`.

4. **ML-based field extraction.** Replace regex with a document understanding model for higher accuracy and coverage, especially for scanned PDFs.

5. **Numeric value column.** Store a parsed `numeric_value` alongside `original_value` for `number` typed fields to make range queries correct and efficient.

6. **Vector similarity search.** Generate document embeddings (e.g., from raw_text via a sentence transformer or the Anthropic/GPT APIs) and store them in a `pgvector` column to support "find similar documents" queries.

---

## Known Limitations

- Amount range filters will fail silently if `original_value` is not a valid float string.
- PDF extraction relies on text-layer PDFs; scanned images without OCR will produce empty `raw_text`.
- The regex patterns are illustrative - they cover common field label formats but won't handle all real-world document layouts.
- Media files are served by Django's dev server; in production, they will be served via nginx or a CDN.
