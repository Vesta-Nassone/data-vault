# Data Vault

A Django application for ingesting and processing documents. Upload PDFs or JSON payloads, extract key fields, and enable human review and correction through a lightweight HTMX interface and a RESTful JSON API.

---

## Prerequisites

- Python 3
- PostgreSQL 18
- Django 5

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/Vesta-Nassone/data-vault.git
cd data-vault
python -m venv venv
venv\Scripts\activate
Linux: source venv/bin/activate
pip install -r requirements.txt #make sure you're in the folder with the requirements.txt file.
```

### 2. Create PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE data_vault;"
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a superuser (optional, for admin panel access to manage documents and users)

```bash
python manage.py createsuperuser
```

### 5. Seed test data

```bash
python manage.py seed_data
```

This creates 5 sample documents with fields and pre-applied corrections, plus two demo users:

- `demo` / `demo1234` — uploader
- `reviewer` / `review1234` — reviewer

Use `--clear` to wipe existing data before seeding:

```bash
python manage.py seed_data --clear
```

### 6. Run the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## API Endpoints

All API routes are prefixed with `/api/`.

### Authentication

| Method | Endpoint              | Description                      |
| ------ | --------------------- | -------------------------------- |
| POST   | `/api/auth/register/` | Register new user, returns token |
| POST   | `/api/auth/token/`    | Login, returns token             |

**Register:**

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

**Get token:**

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=alice&password=secret123"
```

### Documents

| Method | Endpoint                 | Description                            |
| ------ | ------------------------ | -------------------------------------- |
| GET    | `/api/documents/`        | List documents (paginated, filterable) |
| GET    | `/api/documents/{id}/`   | Document detail with all fields        |
| POST   | `/api/documents/upload/` | Upload PDF (multipart/form-data)       |
| POST   | `/api/documents/ingest/` | Ingest JSON payload                    |

**List documents with filters:**

```bash
# Filter by form type
curl "http://localhost:8000/api/documents/?form_type=w9"

# Filter by field value
curl "http://localhost:8000/api/documents/?field_value=John"

# Filter by amount range
curl "http://localhost:8000/api/documents/?amount_min=1000&amount_max=5000"

# Filter by date range
curl "http://localhost:8000/api/documents/?uploaded_after=2026-01-01&uploaded_before=2026-12-31"
```

**Upload PDF:**

```bash
curl -X POST http://localhost:8000/api/documents/upload/ \
  -H "Authorization: Token <your-token>" \
  -F "file=@/path/to/document.pdf" \
  -F "form_type=w9"
```

**Ingest JSON:**

```bash
curl -X POST http://localhost:8000/api/documents/ingest/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "form_type": "w9",
    "original_filename": "w9_acme.pdf",
    "fields": [
      {"key": "customer_name", "original_value": "Acme Corp", "data_type": "string", "confidence": 0.95},
      {"key": "amount", "original_value": "1500.00", "data_type": "number", "confidence": 0.92}
    ]
  }'
```

### Fields

| Method | Endpoint            | Description           |
| ------ | ------------------- | --------------------- |
| PATCH  | `/api/fields/{id}/` | Correct a field value |

**Correct a field:**

```bash
curl -X PATCH http://localhost:8000/api/fields/<field-id>/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"corrected_value": "John Smith"}'
```

### Reports

| Method | Endpoint                          | Description                     |
| ------ | --------------------------------- | ------------------------------- |
| GET    | `/api/reports/top-corrections/`   | Top 3 most corrected field keys |
| GET    | `/api/reports/documents-by-type/` | Document count by form type     |

```bash
curl http://localhost:8000/api/reports/top-corrections/

curl "http://localhost:8000/api/reports/documents-by-type/?date_from=2026-01-01&date_to=2026-12-31"
```

---

## UI Routes

| URL                | Description                               |
| ------------------ | ----------------------------------------- |
| `/`                | Home - recent documents                   |
| `/upload/`         | Upload PDF or submit JSON                 |
| `/documents/{id}/` | Document detail with inline field editing |
| `/search/`         | Live search/filter documents              |
| `/login/`          | Login                                     |
| `/register/`       | Register                                  |
| `/admin/`          | Django admin                              |
