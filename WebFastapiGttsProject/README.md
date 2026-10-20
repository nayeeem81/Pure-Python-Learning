# WebFastapiGttsProject

A FastAPI-based web application for generating, processing, and customizing TTS audio using gTTS, PostgreSQL, and a browser-based audio studio interface.

This project converts user input text into speech, stores sentence and word-level metadata in a database, analyzes audio segments, and exposes a lightweight front-end for previewing and editing generated audio.

## Overview

The project combines:

- Python backend with FastAPI
- Google Text-to-Speech (`gTTS`) generation
- PostgreSQL + SQLAlchemy async models
- Word and sentence timeline processing
- JavaScript-driven browser audio controls
- HTML templates rendered with Jinja2
- Audio processing with `pydub`

The application is organized into a backend API layer, a web view layer, a database layer, and static frontend assets.

## Key Features Delivered

- Real-time text-to-speech generation from user text
- Sentence-level audio generation and persistence
- Word-by-word segmentation and metadata generation
- Frequency and amplitude adjustment endpoints
- Structured audio timeline stored as JSON metadata
- Secure database-backed history tracking for sentence and word modifications
- Browser UI for audio preview and studio actions
- Static asset and media serving for generated project files
- Integration between Python backend logic and frontend audio players

## Project Architecture

```text
WebFastapiGttsProject/
├── api/
│   ├── __init__.py
│   ├── agent.py
│   ├── dependencies.py
│   ├── frequency.py
│   ├── process.py
│   ├── routerwords.py
│   ├── routes.py
│   └── studio.py
├── data/
│   ├── __init__.py
│   ├── database.py
│   └── model.py
├── project/
│   └── generated/
├── static/
│   ├── js/
│   ├── scripts/
│   ├── wavesurfer.min.js
│   ├── regions.min.js
│   ├── logo.png
│   └── favicon.ico
├── templates/
│   ├── about.html
│   ├── editor.html
│   ├── index.html
│   ├── layout.html
│   └── studio.html
├── views/
│   ├── __init__.py
│   ├── view_routes.py
│   ├── canvas_utility/
│   ├── canvasapps/
│   └── chordapps/
├── config.py
├── main.py
├── requirements.txt
├── README.md
└── WebFastapiGttsProject.pyproj
```

## Main Components

### 1. Application Entry Point

`main.py`

- Initializes the FastAPI application
- Ensures required directories exist (`project/generated` and `/static`)
- Mounts static directories for `/project` and `/static`
- Includes both view routes and API routers
- Manages PostgreSQL database bootstrapping using async SQLAlchemy

Key responsibilities:

- verifies database existence
- creates ORM tables with `Base.metadata.create_all`
- serves frontend assets and generated audio files

### 2. Configuration

`config.py`

Contains application-wide config values such as:

- `SECRET_KEY`
- `APP_HOST`, `APP_PORT`, `APP_ENV`
- PostgreSQL credentials and database name
- `DATABASE_URL` built using AsyncPG and SQLAlchemy

Default database configuration uses PostgreSQL on localhost:

```python
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gttstunevolume_db")
```

### 3. API Layer

`api/routes.py`

This is the central registry that includes all sub-routers:

```python
api_router.include_router(process_router)
api_router.include_router(agent_router)
api_router.include_router(studio_router)
api_router.include_router(frequency_router)
api_router.include_router(router_words)
```

Each router is responsible for a different feature area.

#### `api/agent.py`

Handles direct speech generation routes. Uses `gTTS` to create audio in memory and return it as a streaming response.

Endpoints include:

- `GET /agent/generate-tts`
- `GET /agent/play-file/{filename}`

This module is responsible for:

- creating speech audio from text
- streaming audio back to the client
- optionally caching sentence entries in the database

#### `api/process.py`

This module manages the core generation workflow for speech processing.

It receives text input, creates a `Sentence` record, then launches a background task that:

- saves the sentence audio as MP3
- splits the audio into word segments using `pydub`
- creates metadata JSON with timing information
- stores word-level files in `project/generated/segments`
- writes database records for sentence and words

Endpoint:

- `POST /process/generate-speech-processing`

Request example:

```json
{
  "text": "Hello world from the audio studio"
}
```

The response includes:

- processing status
- sentence ID
- expected paths for audio and metadata files

#### `api/routerwords.py`

This router handles word parsing and audio modification logic.

Features:

- parsing sentence text into word entries
- saving word order in database
- applying pitch and volume tweaks to audio segments
- writing modified word files
- generating updated sentence metadata

Endpoints:

- `POST /words/parse/{sentence_id}`
- `POST /words/consolidate-modifications`

This module is the heart of the customization pipeline. It updates both the generated audio and the metadata timeline.

#### `api/frequency.py`

This is dedicated to pitch/frequency adjustment logic.

It lets the app change the frequency of an audio segment and reassemble the sentence:

- `POST /frequency/update-frequency`

It works by:

- loading the sentence metadata JSON
- locating the target word in the timeline
- modifying that word's frequency
- rebuilding the composite sentence audio
- updating the database and metadata artifacts

#### `api/studio.py`

This module exposes studio engineering endpoints for audio mixing and streaming.

- `POST /studio/mix`
- `GET /studio/stream-track`

It supports the concept of layering tracks and streaming results to the browser. The code has a mixing skeleton that can be expanded with full audio-overlap implementations.

### 4. Database Layer

`data/database.py`

Creates the asynchronous database engine and session factory:

```python
engine = create_async_engine(config.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
```

This project uses PostgreSQL with:

- `sqlalchemy[asyncio]`
- `asyncpg`
- async database sessions

`data/model.py`

Defines the persistent database schema.

Model list:

- `Sentence`
- `Word`
- `SentenceHistory`
- `WordHistory`

Important fields:

```python
class Sentence(Base):
    __tablename__ = "sentence"
    id
    text_content
    audio_bytes
    mp3_file_path
    original_sentence_json
    modified_sentence_json
    version
    modified_at
```

```python
class Word(Base):
    __tablename__ = "words"
    id
    sentence_id
    text_content
    word_order
    audio_bytes
    mp3_file_path
```

These models support:

- sentence-level storage of text and audio
- word-level segmentation and audio files
- full history snapshots for auditing and versioning
- mapping of generated metadata in JSONB fields

### 5. View Layer and HTML

`views/view_routes.py`

This module maps browser routes to HTML pages using Jinja2 templates.

Routes:

- `/` -> home page
- `/audio-studio` -> studio page
- `/word-editor` -> editor page
- `/about` -> about page

These pages are rendered using:

```python
templates = Jinja2Templates(directory=BASE_DIR / "templates")
```

#### HTML Templates

`templates/index.html`

- landing page with feature summary
- describes capabilities of the app

`templates/studio.html`

- simple audio studio layout
- includes live text input for TTS
- master audio player UI
- loads WaveSurfer and app JS

`templates/layout.html`

- shared page shell and navigation layout

`templates/editor.html`

- likely used for word or text editing workspace

`templates/about.html`

- descriptive project or author information page

### 6. Frontend JavaScript and Static Assets

`static/`

This directory contains assets consumed by the front-end.

Key frontend assets:

- `static/js/studio-engine.js`
- `static/wavesurfer.min.js`
- `static/regions.min.js`
- `static/scripts/` (Bootstrap/jquery support)

`studio-engine.js` is the main browser behavior file. It handles the TTS and media interactions in the studio page.

Typical browser behavior includes:

- reading the text input
- invoking the backend `/agent/generate-tts` endpoint
- setting the returned audio stream into the browser player
- controlling audio playback and rendering

### 7. gTTS and Audio Processing Workflow

The system relies heavily on the following libraries:

- `gTTS` for Google-powered speech synthesis
- `pydub` for audio segmenting and reassembly
- `AudioSegment` for word and sentence audio transformations
- `jinja2` for HTML rendering
- `sqlalchemy` for database object mapping

Example workflow:

1. User enters a text string.
2. Backend calls `gTTS(text=text, lang='en')`.
3. Audio is generated in memory or saved to a file.
4. The sentence is split into words.
5. Each word is stored as a segment and metadata entry.
6. Frequency, pitch, or amplitude changes can be applied.
7. The final consolidated audio is exported as a new MP3.
8. Results are persisted to PostgreSQL and saved in `project/generated`.

## Runtime Flow

The project follows a clear flow:

1. Start app with `uvicorn main:app --reload`
2. Postgres auto-check ensures the database exists
3. SQLAlchemy models are created if missing
4. Browser requests the home or studio page
5. Front-end triggers backend TTS routes
6. Audio is generated, segmented, and stored
7. Metadata JSON tracks timing and changes
8. Users can reprocess words with audio tuning

## Setup and Run

### Requirements

The project dependencies are listed in `requirements.txt`.

```bash
fastapi
uvicorn
httpx
python-multipart
pydantic-settings
aiofiles
pip
gTTS
pygame
moviepy
Pillow
orjson
pydub
jinja2
audioop-lts
passlib
pyjwt[crypto]
sqlalchemy[asyncio]
asyncpg
python-jose[cryptography]
```

### Install

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run the server

```bash
python main.py
```

or

```bash
uvicorn main:app --reload
```

The application is typically served at:

```text
http://127.0.0.1:8000
```

### Access the app

- Home page: `http://127.0.0.1:8000/`
- Audio studio: `http://127.0.0.1:8000/audio-studio`
- Word editor: `http://127.0.0.1:8000/word-editor`
- About page: `http://127.0.0.1:8000/about`

## Notes About the Current Project State

This application demonstrates an advanced audio-processing workflow using FastAPI and gTTS. It is more than a simple speech generator because it includes:

- word timeline generation
- file-based asset management
- metadata modeling
- database-backed persistence
- route-driven customization
- modular backend structure

The codebase reflects a learning and experimentation project that achieves a complete TTS + audio customization architecture with a web UI.

## Summary

`WebFastapiGttsProject` is a full-stack Python application that combines speech generation, audio engineering, database persistence, and a browser-based UI. It uses FastAPI for the application server, gTTS for speech synthesis, pydub for audio segmenting, SQLAlchemy + PostgreSQL for data storage, and HTML/JavaScript for the frontend experience.

It delivers a practical pipeline for:

- generating audio from text
- splitting content into word-level segments
- customizing pitch and volume
- saving and rebuilding audio projects
- browsing the generated audio in the browser

## License

This project is intended for educational and personal development use unless otherwise specified by the repository owner.

---

If you want, I can also produce:

1. a shorter GitHub-ready README version,
2. a more professional enterprise-style README, or
3. a README rewritten in a cleaner markdown format ready to paste directly into your repository.
