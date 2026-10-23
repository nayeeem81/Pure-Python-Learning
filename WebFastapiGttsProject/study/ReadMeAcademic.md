# WebFastapiGttsProject

A full-stack text-to-speech and audio engineering web application built with FastAPI, PostgreSQL, and Google Text-to-Speech (gTTS). The system converts textual input into spoken audio, segments the generated audio into word-level components, stores sentence and word metadata in a relational database, and exposes a browser-based interface for speech generation and modification workflows.

This project was developed as a learning-oriented application that combines backend web development, speech synthesis, audio processing, and database-driven application design. It demonstrates how a Python-based service can integrate speech generation, file management, structured metadata modeling, and front-end interface orchestration into a unified digital audio workflow.

## 1. Project Objective

The primary goal of WebFastapiGttsProject is to build a lightweight but extensible TTS application capable of:

- generating spoken audio from plain text
- storing generated voice assets for later retrieval
- converting speech output into manageable word segments
- tracking sentence and word metadata
- enabling frequency and amplitude adjustments for audio experimentation
- presenting a browser interface for audio interaction and playback

The project emphasizes both functional speech generation and educational understanding of how backend systems and audio processing pipelines can work together.

## 2. System Overview

The application consists of four major layers:

1. Backend web server
   - FastAPI application
   - API routes for audio generation and processing
   - Jinja2 view endpoints for HTML rendering

2. Speech generation engine
   - gTTS for generating text-to-speech output
   - pydub for audio segmentation and reconstruction

3. Data layer
   - PostgreSQL database
   - SQLAlchemy async ORM models
   - sentence and word tracking with historical snapshots

4. Frontend and media layer
   - HTML templates
   - JavaScript-driven audio player and control logic
   - static resources and generated media files

Together, these layers create a platform where text can be transformed into audio projects and manipulated at a detailed word-by-word level.

## 3. Functional Features

The system delivers the following core capabilities:

- Text-to-speech generation using Google TTS
- Audio streaming back to the browser
- Database persistence of sentence content and generated audio
- Word-level segmentation of the spoken sentence
- JSON metadata generation describing timing and word segments
- Audio processing for pitch and amplitude adjustment
- Rebuilt speech output after modifications
- Audio studio interface for live audio generation
- Structured project output stored in generated media folders

In addition, the system maintains a history of sentence and word records, enabling version tracking and future extensibility for editing workflows and audio audits.

## 4. Architecture and Project Structure

The project is organized into modular directories to separate concerns:

```text
WebFastapiGttsProject/
├── api/
│   ├── agent.py
│   ├── frequency.py
│   ├── process.py
│   ├── routerwords.py
│   ├── routes.py
│   ├── studio.py
│   └── dependencies.py
├── data/
│   ├── database.py
│   ├── model.py
│   └── __init__.py
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
│   ├── view_routes.py
│   ├── canvas_utility/
│   ├── canvasapps/
│   └── chordapps/
├── config.py
├── main.py
├── requirements.txt
├── README.md
├── WebFastapiGttsProject.pyproj
├── .gitignore
└── static/
```

This structure supports clear separation between:
- API logic
- data models
- project media generation
- frontend templates
- browser-side logic

## 5. Backend and Routing Design

The core application is initialized in main.py, which performs the following tasks:

- creates the FastAPI application
- ensures the required directories exist
- mounts static URL routes for generated files and frontend assets
- verifies database availability
- creates missing database tables
- registers API and view routers

The application uses a central router aggregation through api/routes.py, which includes multiple sub-routers:

- process router
- agent router
- studio router
- frequency router
- word-processing router

This modular router approach keeps the backend organized and makes the application easier to extend with additional audio or speech features.

## 6. API Layer

### 6.1 Agent API

The agent layer is responsible for direct speech generation and streaming audio data to clients.

Core responsibilities:
- generate speech from a text input
- return audio content in a streaming format
- optionally store sentence records in the database
- serve audio files from the local project directory

The agent endpoints support:
- live TTS generation
- local file playback
- direct audio delivery to the browser

### 6.2 Process API

The process API implements the main TTS generation workflow.

The workflow includes:
1. receiving a text input
2. creating a sentence record
3. generating an MP3 using gTTS
4. splitting the speech into word segments
5. writing metadata JSON describing the timeline
6. storing per-word audio files
7. linking the results to the database

This stage is important because it transforms a simple text input into a structured digital audio project with defined sound segments and metadata.

### 6.3 Frequency API

The frequency API supports audio tuning operations.

It is designed to:
- locate a word in the sentence timeline
- adjust the pitch or frequency of that word
- rebuild the processed sentence audio
- update metadata and database records

This provides a strong foundation for experimentation with sound design and speech modification.

### 6.4 Word Processing API

This route handles parsing and post-processing of sentence text into word-level units. It supports:

- extraction of words from sentence text
- insertion of word rows into the database
- tracking word order
- modification and consolidation of word segments
- database snapshot retention for revision history

This is one of the most important technical parts of the project because it enables detailed manipulation of the generated voice.

### 6.5 Studio API

The studio API manages audio engineering-style operations such as:

- mixing multiple audio layers
- streaming audio tracks to the client
- preparing a more advanced audio mini-studio interface

This module acts as a bridge between the general speech generation workflow and more advanced sound-processing features.

## 7. Database Design

The project uses PostgreSQL with SQLAlchemy asynchronously. This choice supports efficient database access and is suitable for a Python async application.

The database connection is defined in data/database.py and the configuration is supplied by config.py. These settings include credentials, database host, port, database name, and application environment.

Core database entities:

- Sentence
- Word
- SentenceHistory
- WordHistory

### Sentence model
Stores the primary text and generated media output for a given input sentence.

Fields include:
- text content
- audio bytes
- MP3 file path
- original metadata JSON
- modified metadata JSON
- versioning metadata

### Word model
Stores individual words derived from the sentence, with per-word ordering and audio payloads.

Fields include:
- word order
- sentence reference
- textual content
- audio bytes
- file path for the generated word segment

### History models
History tables preserve previous sentence and word states before modification, allowing the application to track iterative sound engineering changes over time.

This makes the project more robust as a learning exercise in relational design, data retention, and system evolution.

## 8. Frontend Design

The frontend uses Jinja2 templates and static assets to render a browser-based interface.

### Templates
The templates folder contains the following primary pages:

- index.html: landing page and project overview
- studio.html: TTS generation interface
- editor.html: editing/workflow area
- layout.html: shared UI structure
- about.html: informational page

### Audio Studio Interface
The main studio page contains:
- a text input field
- a button to generate speech
- an audio player element
- support for external audio libraries such as WaveSurfer

The browser and backend communicate through API routes, allowing the generated speech to be delivered directly to the browser for playback.

## 9. Frontend JavaScript

The static frontend includes JavaScript resources such as:

- studio-engine.js
- WaveSurfer library
- Regions plugin
- supporting jQuery/Bootstrap scripts

These assets are used to create an interactive front-end experience. The JavaScript layer handles:
- triggering TTS generation
- reading user input
- passing the text to the backend
- setting the generated audio stream as the source for the media player
- enabling front-end controls for sound playback and interactions

This integration demonstrates the use of JavaScript in a web application to enrich the backend-generated audio experience.

## 10. gTTS and Audio Processing

The project relies on gTTS, a Python library that interfaces with Google Text-to-Speech for converting text into natural-sounding speech.

The audio workflow typically follows this sequence:

1. Input text is submitted through the web application.
2. The backend calls gTTS to generate a speech object.
3. Audio is saved as an MP3 or written to an in-memory buffer.
4. pydub slices the generated speech into smaller word-level segments.
5. Each segment is stored with metadata and file paths.
6. The system can rebuild or modify the speech output.
7. The final result is saved or returned to the user as a playable audio asset.

This combination of gTTS and pydub gives the project a practical audio engineering workflow while also serving as a good example of speech-generation pipeline design.

## 11. Key Technical Contributions

This project demonstrates several important software engineering principles:

- modular backend structure
- clear separation of concerns
- asynchronous database interaction
- metadata-driven audio processing
- versioning of generated content
- integration of frontend assets with backend API services
- use of cloud-based speech synthesis through gTTS
- structured management of generated artifacts in local project folders

It is not merely a speech synthesizer; it is a complete mini-platform for generated audio assets and project metadata.

## 12. Educational and Research Value

From an academic and project presentation perspective, WebFastapiGttsProject is valuable because it combines multiple disciplines:

- Python web application development
- REST API design
- relational database modeling
- data persistence and version tracking
- audio signal processing concepts
- multimedia web application design
- asynchronous backend architecture

This interdisciplinary structure makes the project especially suitable for demonstrating software engineering practice in a real-world, application-oriented context.

## 13. Setup and Execution

The project includes the required dependencies in requirements.txt, and can be run locally with:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

or:

```bash
uvicorn main:app --reload
```

Once started, the application is typically available at:

```text
http://127.0.0.1:8000
```

The frontend can be accessed through pages such as:
- home page
- audio studio page
- word editor
- about page

## 14. Conclusion

WebFastapiGttsProject represents a practical demonstration of how to combine web application development, speech synthesis, and audio engineering within a single Python system. It provides a strong foundation for learning how backend APIs, database persistence, and frontend interaction can be integrated into a real-world multimedia project.

The project is particularly valuable as an educational prototype because it shows how a text-to-speech system can evolve from a simple voice-generation tool into a more structured audio-processing platform with database-backed asset management and user interaction.

This version is designed for academic presentation and project storytelling, and it intentionally emphasizes the technical and conceptual value of the overall system.
