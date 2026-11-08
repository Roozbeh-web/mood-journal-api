# Mood Journal API

A private diary REST API that analyzes the mood of each entry and exposes per-user statistics.

## Features

- Token-based authentication (one token per user)
- Create, list, retrieve, update, and delete diary entries
- Server-side mood scoring from free-text entries
- Per-user statistics: total entries, average mood, and sentiment breakdown
- Strict per-user data isolation: users can only ever access their own entries
- Unit tests for the analyzer and integration tests for the API

## Tech Stack

- Python 3
- Django
- Django REST Framework
- MariaDB
- openpyxl (used by the lexicon build script to read the PerSent Excel file)
- django-filter

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Roozbeh-web/mood-journal-api.git
cd mood-journal-api
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create the database and user in MariaDB

```sql
CREATE DATABASE moodjournal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mooduser'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON moodjournal.* TO 'mooduser'@'localhost';
FLUSH PRIVILEGES;
```

5. Set your database credentials in ```config/settings.py``` (or via environment variables).

6. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

7. Run migrations:

```bash
python manage.py migrate
```

8. Create a superuser:

```bash
python manage.py createsuperuser
```

9. Run the server:

```bash
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/token/` | Obtain an auth token with username and password |
| GET | `/api/entries/` | List the authenticated user's entries |
| POST | `/api/entries/` | Create a new entry |
| GET | `/api/entries/<id>/` | Retrieve one of the user's entries |
| PATCH | `/api/entries/<id>/` | Update an entry's text (score is recomputed) |
| DELETE | `/api/entries/<id>/` | Delete an entry |
| GET | `/api/entries/stats/` | Per-user aggregate statistics |

All endpoints except `/api/auth/token/` require the header:

```
Authorization: Token <your-token>
```

## Example

Obtain a token: 

```
POST /api/auth/token/
Content-Type: application/json

{"username": "alice", "password": "secret"}
```

Response:

```json
{"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

Create an entry:

```
POST /api/entries/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json

{"text": "امروز خیلی خوب و عالی بود"}
```

Response:

```json
{
    "id": 1,
    "text": "امروز خیلی خوب و عالی بود",
    "mood_score": 1.0,
    "created_at": "2026-11-08T12:00:00Z"
}
```

Get statistics:

```
GET /api/entries/stats/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

Response:

```json
{
    "total_entries": 12,
    "average_mood": 0.25,
    "positive_entries": 6,
    "negative_entries": 3,
    "neutral_entries": 3
}
```

## How Mood Scoring Works

Each entry's text is tokenized with a Unicode-aware regular expression that recognizes both Latin and Persian/Arabic word characters. However, only Persian words are scored: the merged sentiment lexicon contains Persian entries from PerSent and the curated colloquial list, with no English words. Latin-script tokens are recognized as tokens but will not match the lexicon, so they contribute nothing to the score.

- **PerSent** — a published Persian sentiment lexicon, filtered to words with a polarity score of at least 0.3 (positive) or at most -0.3 (negative).

- **A curated colloquial lexicon** — everyday Persian words and verb forms that the academic PerSent lexicon does not cover, organized by emotion category.

The score is computed as:

```
(positive_count - negative_count) / (positive_count + negative_count)
```

This produces a value in `[-1.0, 1.0]`, where `0.0` means neutral or no recognized sentiment words. The score is always computed server-side and cannot be set by the client.

The merged lexicon is stored in `entries/data/lexicon.json`. It is generated from PerSent by `scripts/build_lexicon.py` using `openpyxl` to read the Excel source file.

## Running Tests

```bash
python manage.py test entries
```

The test suite covers:

- Mood analyzer behavior (7 tests): positive, negative, neutral, empty, mixed, case-insensitivity, score bounds
- API behavior (8 tests): authentication, entry creation, server-side scoring, ownership enforcement, per-user isolation on read, update and delete
- Statistics endpoint (4 tests): authentication, empty state, sentiment bucketing, per-user isolation

## Acknowledgments

This project uses the **PerSent** Persian sentiment lexicon, developed by the authors of the PerSent paper. PerSent is distributed free for non-commercial academic use and is **not** redistributed in this repository. To regenerate the lexicon file from scratch, download PerSent from its official source and run `python scripts/build_lexicon.py`.

- PerSent: http://www.gelbukh.com/resources/persent/

## Author

Roozbeh
https://github.com/Roozbeh-web