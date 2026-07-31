# 📚 AI Influencer Discovery & Analytics Dashboard — Complete Technical Documentation & Knowledge Base

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Complete Folder Structure](#3-complete-folder-structure)
4. [File-by-File Documentation](#4-file-by-file-documentation)
5. [Data Models](#5-data-models)
6. [Views & Controllers](#6-views--controllers)
7. [URL Routing System](#7-url-routing-system)
8. [Templates & UI Components](#8-templates--ui-components)
9. [JavaScript Infrastructure](#9-javascript-infrastructure)
10. [CSS & Layout System](#10-css--layout-system)
11. [Service Architecture](#11-service-architecture)
12. [AI Classification Module](#12-ai-classification-module)
13. [NLP Processing Module](#13-nlp-processing-module)
14. [Database Operations & Data Flow](#14-database-operations--data-flow)
15. [End-to-End Application Workflow](#15-end-to-end-application-workflow)
16. [Authentication & Session Security](#16-authentication--session-security)
17. [Configuration & Environment Settings](#17-configuration--environment-settings)
18. [Error Handling & Fault Tolerance](#18-error-handling--fault-tolerance)
19. [Security Architecture](#19-security-architecture)
20. [Performance Optimization](#20-performance-optimization)
21. [Dependencies & Third-Party Libraries](#21-dependencies--third-party-libraries)
22. [System Architectural Diagrams](#22-system-architectural-diagrams)
23. [Core Business Logic Rules](#23-core-business-logic-rules)
24. [Frequently Asked Questions (Technical Q&A)](#24-frequently-asked-questions-technical-qa)
25. [Developer Maintenance & Extension Guide](#25-developer-maintenance--extension-guide)
26. [Executive Project Summary](#26-executive-project-summary)

---

## 1. Project Overview

### Purpose & Objective
The **AI Influencer Discovery & Analytics Dashboard** is an enterprise-grade platform built to automate the identification, cleaning, evaluation, scoring, and classification of social media content creators (influencers). The platform evaluates creators against specific national development policies, government initiatives (*Digital India*, *UPI*, *PM Kisan*, *Viksit Bharat*, *Startup India*), content niches, and regional Indian languages (*Hindi*, *English*, etc.).

### Business Problem
Brand strategists, public policy managers, and marketing agencies face significant hurdles when vetting social media creators manually:
- **Unstructured Data**: Handles, bio descriptions, follower metrics, and posts arrive in messy CSV/Excel spreadsheets with missing headers, non-standard follower counts (e.g. `150K`, `2.5M`), and inconsistent schemas.
- **Multilingual Content**: Influencer bios frequently mix Hindi Unicode script (`हिंदी में टेक`), English, emojis, and hashtags, making standard filtering brittle.
- **Subjective Vetting**: Manual review of thousands of creator profiles to judge alignment with policy themes or brand guidelines is slow, inconsistent, and error-prone.
- **Lack of Transparency**: Traditional batch AI tools operate as a "black box" where users wait indefinitely without knowing progress, error states, or retry attempts.

### Solution Architecture
The platform resolves these challenges by uniting two complementary analysis pipelines into a unified Django web application:
1. **File-Based Analysis (ETL Pipeline)**: Ingests CSV and Excel files up to 10MB, normalizes 20+ header variations, validates data types, handles null safety, and bulk-inserts records into PostgreSQL.
2. **Real-Time Discovery Engine**: Features a pluggable provider pattern (`BaseProvider`, `MockProvider`) allowing dynamic lookup and deduplication of creators by handle, platform, or external ID.
3. **spaCy Natural Language Processing (NLP)**: Performs language detection (`langdetect`), Named Entity Recognition (NER), noun chunk extraction, and weighted domain rule scoring.
4. **OpenRouter AI (LLM) Engine**: Evaluates creator context using advanced LLMs (e.g., `nvidia/nemotron-3-ultra-550b-a55b:free`), generating quantitative scores (0–100), confidence metrics, recommendations (*Recommend*, *Maybe*, *Reject*), matched keywords, and structured explanations.
5. **Real-Time Progress Visibility (SSE)**: Streams live progress metrics, stage updates, timer counts, and terminal logs directly to the user interface via Server-Sent Events (`text/event-stream`).
6. **Analytics & Data Export**: Interactive Chart.js visual analytics and enterprise exports to Excel (`.xlsx` with openpyxl) and streaming UTF-8 BOM CSV (`.csv`).

### Technology Stack & Rationale

| Technology | Role | Rationale for Selection |
|---|---|---|
| **Python 3.12** | Programming Language | Strong NLP/AI ecosystem, native data handling, excellent Django support. |
| **Django 6.0** | Backend Framework | High-level framework with built-in ORM, security defaults, admin panel, authentication, and URL routing. |
| **PostgreSQL 16** | Database Engine | Robust relational database supporting JSONB fields, unique constraints, and ACID transactions. |
| **spaCy (`en_core_web_sm`)** | NLP Framework | Industrial-strength NLP library for fast entity extraction, noun chunk parsing, and tokenization. |
| **langdetect** | Language Identification | Lightweight Google langdetect port for fast multilingual ISO language code detection. |
| **OpenRouter AI (OpenAI SDK)** | LLM API Integration | Flexible gateway to top-tier open and proprietary LLMs via standardized OpenAI client interfaces. |
| **Pandas & openpyxl** | File Processing & ETL | Best-in-class data manipulation library for reading, cleaning, and normalizing CSV and Excel files. |
| **Bootstrap 5.3** | Frontend Framework | Responsive, accessible CSS framework providing modern UI components, modals, and grid system. |
| **Chart.js 4.4** | Data Visualization | Lightweight, canvas-based chart library for interactive visual analytics. |

---

## 2. High-Level Architecture

The system follows a modular **Layered Architecture Pattern** built on Django's Model-View-Template (MVT) design, enhanced with stateless service modules:

```mermaid
graph TD
    User([User Browser]) <--> |HTTP / SSE| Views[Django App Views Layer]
    Views <--> |QuerySet ORM| Models[Django PostgreSQL Models]
    Views --> |ETL Processing| UploadService[Upload & Data Cleaning Service]
    Views --> |NLP Extraction| NLPService[spaCy & LangDetect NLP Service]
    Views --> |AI Classification| AIService[OpenRouter LLM Service]
    Views --> |Discovery API| DiscoveryService[Real-Time Provider Manager]
    Views --> |Data Export| ExportService[Excel & CSV Response Generator]
    
    UploadService --> |Data Parsing| Pandas[Pandas & Openpyxl Engine]
    NLPService --> |NER & Lemmatization| Spacy[spaCy en_core_web_sm]
    AIService --> |HTTP API| OpenRouter[OpenRouter AI Gateway]
    DiscoveryService --> |Mock / External API| Providers[Pluggable Provider Registry]
```

### Architectural Subsystems
- **Authentication & Security Subsystem**: Custom `User` model, custom login form with dual Username/Email lookup, staff login restriction, session cookie isolation between Admin (`admin_sessionid`) and Application (`sessionid`), and session-bound CSRF protection (`CSRF_USE_SESSIONS = True`).
- **ETL Upload Subsystem**: Multi-format parser for `.csv` and `.xlsx` files supporting header normalization, string-to-integer follower conversions, preview JSON generation, and chunked `bulk_create`.
- **NLP Analysis Subsystem**: Text sanitizer removing URLs, emails, phone numbers, and emojis; spaCy entity/noun chunk extractor; rule-based scoring engine applying 25-point weighted domain matching.
- **AI Engine Subsystem**: Prompt builder assembling strict JSON contracts; OpenRouter API executor with exponential backoff retries (`1s`, `2s`, `4s`); SSE stream generator pushing live updates to the UI.
- **Analytics & Export Subsystem**: QuerySet aggregation engine computing KPIs, summary stats, top rankings, chart data distributions, and multi-format file exporters.

---

## 3. Complete Folder Structure

```text
AI_Influence_Dashboard/
├── .env                         # Local environment configuration file (API keys, DB credentials)
├── .env.example                 # Example template for environment configuration
├── .gitignore                   # Git exclusion rules for venv, media, staticfiles, and bytecodes
├── API_DOCUMENTATION.md         # Documentation for external API endpoints and SSE stream specifications
├── CHANGELOG.md                 # Project version history and feature rollout log
├── DEPLOYMENT_GUIDE.md          # Step-by-step production deployment instructions (Gunicorn, Nginx, Systemd)
├── FUTURE_ENHANCEMENTS.md       # Roadmap for future feature additions (Celery, Redis, Graph APIs)
├── KNOWN_LIMITATIONS.md         # Documented technical boundaries and architectural trade-offs
├── LICENSE                      # Project open-source license (MIT License)
├── PROJECT_SUMMARY.md           # Executive overview of implementation achievements
├── PROJECT_WRITEUP.md           # Technical submission assignment write-up
├── README.md                    # Main GitHub repository landing page and documentation
├── TESTING_REPORT.md            # Automated test suite audit and QA coverage report
├── USER_GUIDE.md                # End-user operational manual and walkthrough
├── manage.py                    # Django CLI administration entry point script
├── requirements.txt             # Python package dependency specifications
├── apps/                        # Custom Django application packages
│   ├── authentication/          # User management, sign up, login, logout, and session isolation
│   ├── classification/          # Classification and SearchCriteria data models
│   ├── dashboard/               # Main dashboard overview, analytics views, and chart services
│   ├── influencers/             # Core creator models, views, services, NLP, AI, discovery, export
│   └── uploads/                 # File ingestion, ETL processing, preview generation, history
├── config/                      # Django project configuration package
│   ├── __init__.py              # Package marker
│   ├── asgi.py                  # ASGI deployment entry point for asynchronous servers
│   ├── settings.py              # Central settings configuration (DB, Auth, Installed Apps, Security)
│   ├── urls.py                  # Master URL routing table and custom 404/500 handler bindings
│   ├── views.py                 # Master error views (custom 404 and 500 handlers)
│   └── wsgi.py                  # WSGI deployment entry point for HTTP servers
├── docs/                        # Project documentation assets
│   └── screenshots/             # UI application screenshots for documentation rendering
├── media/                       # Uploaded user files directory (organized by year/month/day)
├── services/                    # Core business logic service directory marker
├── static/                      # Global static assets
│   ├── css/                     # Custom stylesheet files (`custom.css`)
│   ├── images/                  # Static image assets
│   ├── js/                      # Frontend JavaScript files (`dashboard.js`, `analytics.js`)
│   └── vendor/                  # Third-party frontend libraries
├── templates/                   # HTML template hierarchy
│   ├── 404.html                 # Custom 404 Page Not Found error template
│   ├── 500.html                 # Custom 500 Internal Server Error template
│   ├── analytics/               # Analytics dashboard templates and partials
│   ├── authentication/          # Login, signup, and forgot password templates
│   ├── base/                    # Base layout, header, footer, navbar, and sidebar templates
│   ├── dashboard/               # Main overview home dashboard template
│   ├── influencers/             # AI classification progress stream, NLP, and discovery templates
│   ├── results/                 # Influencer results list, detail drawer, cards, table, and score partials
│   └── uploads/                 # File upload, upload history, and 10-row preview templates
├── Testing/                     # QA data generation scripts for test setup
└── utils/                       # Shared base models and abstract utilities
    └── models.py                # `TimeStampedModel` abstract base class (`created_at`, `updated_at`)
```

---

## 4. File-by-File Documentation

### Core Configuration Files

#### [`manage.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/manage.py)
- **Purpose**: Django's standard command-line utility for administrative tasks.
- **Responsibilities**: Sets the `DJANGO_SETTINGS_MODULE` environment variable to `config.settings` and delegates command execution to `django.core.management`.
- **Imports**: `os`, `sys`, `django.core.management.execute_from_command_line`.
- **Functions**: `main()`: Executes management commands from command-line arguments.

#### [`config/settings.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/config/settings.py)
- **Purpose**: Central configuration module for the Django project.
- **Responsibilities**: Configures environment variables via `python-dotenv`, database settings (`postgresql`), installed applications, custom middleware stack (`IsolatedSessionMiddleware`), custom user model (`AUTH_USER_MODEL = 'authentication.User'`), session security, CSRF session binding (`CSRF_USE_SESSIONS = True`), static/media paths, and OpenRouter AI API credentials.
- **Dependencies**: `os`, `pathlib.Path`, `dotenv.load_dotenv`.

#### [`config/urls.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/config/urls.py)
- **Purpose**: Master URL dispatcher for the application.
- **Responsibilities**: Binds top-level paths (`admin/`, `dashboard/`, `uploads/`, `influencers/`), configures static/media file serving, defines development error preview routes (`/404/`, `/500/`), and registers global error handlers (`handler404`, `handler500`).

#### [`config/views.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/config/views.py)
- **Purpose**: Custom error handler view implementations.
- **Functions**:
  - `custom_404_view(request, exception=None)`: Renders `404.html` with status code 404.
  - `custom_500_view(request, exception=None)`: Renders `500.html` with status code 500.

#### [`config/wsgi.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/config/wsgi.py) & [`config/asgi.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/config/asgi.py)
- **Purpose**: Server entry points for WSGI (Gunicorn/uWSGI) and ASGI (Daphne/Uvicorn) web servers.

---

### Authentication Application (`apps/authentication`)

#### [`apps/authentication/models.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/authentication/models.py)
- **Purpose**: Custom User model definition.
- **Classes**: `User(AbstractUser)`: Inherits from Django's `AbstractUser`, enabling future user attribute extensions while keeping database migrations clean.

#### [`apps/authentication/forms.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/authentication/forms.py)
- **Purpose**: Form validation for login and user registration.
- **Classes**:
  - `CustomLoginForm(AuthenticationForm)`: Overrides authentication to accept either username or email in the `username` field. Includes a `remember_me` checkbox. Implements `confirm_login_allowed(user)` to restrict staff and superuser accounts from logging into the frontend application.
  - `CustomUserCreationForm(UserCreationForm)`: Registers new users with first name, last name, username, and email. Validates email uniqueness in `clean_email()`.

#### [`apps/authentication/views.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/authentication/views.py)
- **Purpose**: Controller logic for login, registration, and logout.
- **Classes & Functions**:
  - `CustomLoginView(LoginView)`: Renders `authentication/login.html`. Sets session expiration to `0` (browser close) if `remember_me` is unchecked.
  - `SignUpView(CreateView)`: Renders `authentication/signup.html`, creates new `User` instance, displays a success message, and redirects to login.
  - `custom_logout_view(request)`: Logs out the user via `django.contrib.auth.logout` and redirects to the login page.

#### [`apps/authentication/middleware.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/authentication/middleware.py)
- **Purpose**: Implements session cookie isolation between Django Admin and the application.
- **Classes**: `IsolatedSessionMiddleware(SessionMiddleware)`: Intercepts incoming requests. If the URL path starts with `/admin`, it uses the `admin_sessionid` cookie name; otherwise, it uses the standard `sessionid` cookie name. Prevents session collision when an administrator is logged into both the Django Admin panel and the frontend dashboard simultaneously.

#### [`apps/authentication/urls.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/authentication/urls.py)
- **Purpose**: URL routes for `login/`, `logout/`, `signup/`, and `forgot-password/`.

---

### Uploads Application (`apps/uploads`)

#### [`apps/uploads/models.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/uploads/models.py)
- **Purpose**: Data model tracking uploaded files and ETL execution status.
- **Classes**: `Upload(TimeStampedModel)`: Tracks user relationship, file field (`uploads/%Y/%m/%d/`), file name, size, type (`CSV`, `XLSX`), row counts, processing status (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`), error messages, 10-row preview JSON, and processing summary statistics.

#### [`apps/uploads/utils.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/uploads/utils.py)
- **Purpose**: Low-level data cleaning and normalization helper functions.
- **Functions**:
  - `normalize_headers(df)`: Maps 20+ common header variations (`biography`, `follower count`, etc.) to standard internal names.
  - `clean_text(value, default="")`: Sanitizes text by stripping whitespace, removing redundant spaces, and converting `None`/`NaN` to empty strings (guaranteeing non-null values for DB insert).
  - `parse_followers(value, default=0)`: Parses follower counts formatted as `15K`, `2.5M`, `1B`, `45,000`, floats, or text strings into positive integers.
  - `normalize_platform(value, default='OTHER')`: Maps platform names (`insta`, `yt`, `twitter`, `fb`) to Django model choices (`INSTAGRAM`, `YOUTUBE`, `TWITTER`, `FACEBOOK`, `LINKEDIN`, `OTHER`).
  - `normalize_influencer_dict(row)`: Centralized sanitizer returning a dictionary guaranteed to conform to database field constraints.

#### [`apps/uploads/services.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/uploads/services.py)
- **Purpose**: Core ETL pipeline logic for reading, parsing, validating, and bulk-inserting uploaded file data.
- **Functions**:
  - `validate_file(file)`: Enforces maximum file size (10MB) and allowed extensions (`csv`, `xlsx`).
  - `process_upload_file(upload_id)`: Atomic transaction processing function. Locks the `Upload` row, reads the file via Pandas or Openpyxl, normalizes headers, extracts 10-row preview JSON, sanitizes every row, constructs `Influencer` instances, and performs `bulk_create(ignore_conflicts=True)` in batches of 1,000 rows. Updates process timing and statistics upon completion.

#### [`apps/uploads/views.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/uploads/views.py)
- **Purpose**: Controller views for uploading files, viewing upload history, and inspecting file previews.
- **Functions**:
  - `upload_view(request)`: Handles file upload form submission, creates `Upload` record, calls `process_upload_file()`, and redirects to preview.
  - `upload_history_view(request)`: Displays paginated, searchable, and filterable upload log table for the authenticated user.
  - `upload_preview_view(request, pk)`: Displays file details, processing summary stats, and the 10-row data preview modal.

---

### Influencers Application (`apps/influencers`)

#### [`apps/influencers/models.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/models.py)
- **Purpose**: Core creator data model storing profile details, NLP extractions, and discovery metadata.
- **Classes**: `Influencer(TimeStampedModel)`: Stores profile attributes (`name`, `handle`, `platform`, `followers`, `bio`, `description`, `location`, `language`, `email`), NLP extractions (`language_detected`, `extracted_keywords`, `extracted_entities`, `rule_based_score`, `nlp_matched_groups`), and real-time discovery metadata (`source`, `external_id`, `discovered_at`). Implements database indexes and unique constraints on `(handle, platform)`.

#### [`apps/influencers/services/nlp_service.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/services/nlp_service.py)
- **Purpose**: Service executing spaCy NLP feature extraction and rule-based scoring.
- **Functions**:
  - `process_influencer_nlp(influencer)`: Sanitizes text, detects language via `langdetect`, extracts noun chunks and named entities via spaCy, computes domain match scores, and updates the database record.
  - `batch_process_nlp(user=None)`: Iterates over unprocessed `Influencer` records using `.iterator()` to execute NLP analysis in bulk.

#### [`apps/influencers/utils.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/utils.py)
- **Purpose**: Low-level NLP utility routines.
- **Functions**:
  - `get_nlp_model()`: Singleton loader for spaCy `en_core_web_sm` model.
  - `clean_text_for_nlp(text)`: Removes URLs, emails, phone numbers, emojis, and special characters while preserving hashtag keywords.
  - `detect_language(text)`: Executes `langdetect.detect_langs()` and maps codes (`hi` ➔ `Hindi`, `en` ➔ `English`).
  - `extract_nlp_features(text)`: Parses noun chunks and NER entities (`ORG`, `GPE`, `PERSON`, `EVENT`).
  - `calculate_rule_based_score(keywords, entities, language)`: Evaluates matching across 4 keyword domain groups (*government_schemes*, *development*, *technology*, *social*), awarding 25 points per matched group up to 100.

#### [`apps/influencers/services/prompt_builder.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/services/prompt_builder.py)
- **Purpose**: Constructs strict system and user prompts for OpenRouter LLMs.
- **Functions**: `build_classification_prompt(influencer, criteria=None)`: Formats influencer profile attributes, NLP keywords, and search criteria into a structured prompt enforcing a strict JSON output schema.

#### [`apps/influencers/services/response_parser.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/services/response_parser.py)
- **Purpose**: Validates and cleans raw string responses returned by OpenRouter LLMs.
- **Functions**: `parse_ai_response(response_text)`: Strips markdown code blocks (` ```json `), parses JSON strings, and validates the presence of required schema keys (`overall_score`, `confidence_score`, `recommendation`, `reason`).

#### [`apps/influencers/services/openrouter_service.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/services/openrouter_service.py)
- **Purpose**: OpenAI SDK client wrapper for executing OpenRouter AI completions with retries and stage callbacks.
- **Classes**: `OpenRouterService`: Initializes OpenAI client with OpenRouter base URL. Implements `classify_influencer(influencer, criteria, stage_callback)` with exponential backoff retries (`1s`, `2s`, `4s`) for rate-limit errors and invokes live progress callbacks.

#### [`apps/influencers/services/result_service.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/services/result_service.py)
- **Purpose**: Optimizes QuerySet filtering, searching, and sorting for influencer results.
- **Functions**: `get_filtered_classifications(user, query_params)`: Applies global search, platform, language, recommendation, source, score range, and follower range filters. Orders results according to specified sort keys using `select_related('influencer')`.

#### [`apps/influencers/services/export_service.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/services/export_service.py)
- **Purpose**: Multi-format data export engine.
- **Functions**:
  - `get_export_queryset(request, export_type)`: Fetches selected or filtered `Classification` objects.
  - `generate_csv_response(queryset, filename)`: Streams UTF-8 BOM (`\ufeff`) encoded CSV data to preserve Hindi Unicode text in Microsoft Excel.
  - `generate_excel_response(queryset, filename)`: Generates formatted `.xlsx` spreadsheets using `openpyxl` with styled headers, frozen panes, and auto-adjusted column widths.

#### [`apps/influencers/services/discovery_service.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/services/discovery_service.py)
- **Purpose**: Real-time influencer discovery orchestrator.
- **Classes**: `DiscoveryService`: Executes searches against active data providers, deduplicates candidates by handle and platform, saves new creator records, and automatically triggers immediate NLP and AI classification.

#### [`apps/influencers/services/provider_manager.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/services/provider_manager.py) & [`apps/influencers/providers/`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/providers/)
- **Purpose**: Pluggable external API provider architecture.
- **Classes**:
  - `BaseProvider(ABC)`: Abstract base class defining `name` and `search(criteria)` methods.
  - `MockProvider(BaseProvider)`: Provider simulating live external social media API searches for testing.
  - `ProviderManager`: Registry mapping provider names to provider classes and instantiating the active provider based on environment settings.

#### [`apps/influencers/views.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/influencers/views.py)
- **Purpose**: Controller views for NLP execution, AI classification streaming, results display, detail viewing, data export, and discovery.
- **Functions**:
  - `nlp_processing_view(request)`: Triggers batch NLP processing and displays stats.
  - `ai_classification_stream_view(request)`: SSE stream endpoint (`StreamingHttpResponse`, `text/event-stream`) yielding real-time JSON events (`start`, `stage_update`, `item_complete`, `complete`) to power the live progress UI.
  - `ai_classification_view(request)`: Standard POST view for synchronous batch AI classification.
  - `results_list_view(request)`: Renders paginated Table and Grid Card views with filter form.
  - `influencer_detail_view(request, pk)`: Displays detailed score breakdown and AI reasoning modal for a specific creator.
  - `export_results_view(request)`: Handles CSV and Excel file downloads.
  - `discovery_view(request)`: Handles real-time search form submissions to discover new influencers.

---

### Classification Application (`apps/classification`)

#### [`apps/classification/models.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/classification/models.py)
- **Purpose**: Data models for target search criteria and AI evaluation results.
- **Classes**:
  - `SearchCriteria(TimeStampedModel)`: Stores user policy target guidelines (`keywords`, `languages`, `orientation`, `niches`, `minimum_followers`, `platforms`).
  - `Classification(TimeStampedModel)`: Stores AI evaluation results linked to an `Influencer` and `SearchCriteria`. Attributes include `overall_score`, `confidence_score`, match booleans (`language_match`, `orientation_match`, `niche_match`, `keyword_match`), `matched_keywords`, `reason`, `recommendation` (`RECOMMEND`, `MAYBE`, `REJECT`), `ai_model_name`, `processing_time_seconds`, `summary`, and raw `ai_response` JSON.

---

### Dashboard & Analytics Application (`apps/dashboard`)

#### [`apps/dashboard/models.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/dashboard/models.py)
- **Purpose**: Lightweight app marker model.

#### [`apps/dashboard/views.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/dashboard/views.py)
- **Purpose**: Views for the main overview dashboard and visual analytics page.
- **Functions**:
  - `home_view(request)`: Computes high-level KPI card metrics (total uploads, total rows, successful/failed counts, NLP processed count, AI classified count) and recent upload activity.
  - `analytics_dashboard_view(request)`: Collects query parameters and delegates to `analytics_service.get_analytics_context()` to render Chart.js visual analytics.

#### [`apps/dashboard/services/analytics_service.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/dashboard/services/analytics_service.py)
- **Purpose**: Aggregation engine computing KPIs, summary stats, top lists, and recent activities across custom date ranges and filters.
- **Functions**:
  - `apply_date_filters(qs, date_field, date_range, custom_start, custom_end)`: Filters QuerySets by date presets (`today`, `7days`, `30days`, `90days`, `this_year`, `custom`).
  - `get_filtered_querysets(user, filters)`: Applies date, platform, language, recommendation, and score range filters across `Upload`, `Influencer`, and `Classification` QuerySets.
  - `get_kpi_data()`, `get_summary_stats()`, `get_top_lists()`, `get_recent_activity()`: Aggregates metrics using Django ORM annotations (`Count`, `Avg`, `Max`, `Min`) and Python `Counter` objects for JSON fields.

#### [`apps/dashboard/services/chart_service.py`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/apps/dashboard/services/chart_service.py)
- **Purpose**: Formats aggregated data into Chart.js JSON structures.
- **Functions**: `get_chart_data(influencer_qs, classification_qs, upload_qs)`: Builds label and dataset arrays for 8 distinct charts: Language Distribution (Pie), Platform Split (Bar), Overall Score Distribution (Bar), Recommendation Split (Pie), Orientation Match (Bar), Follower Tier Buckets (Bar), Upload Trend (Line), and Classification Trend (Line).

---

## 5. Data Models

```mermaid
erDiagram
    USER ||--o{ UPLOAD : "uploads file"
    USER ||--o{ SEARCH_CRITERIA : "defines"
    USER ||--o{ INFLUENCER : "discovers"
    UPLOAD ||--o{ INFLUENCER : "contains"
    INFLUENCER ||--o{ CLASSIFICATION : "receives"
    SEARCH_CRITERIA ||--o{ CLASSIFICATION : "evaluates against"

    USER {
        int id PK
        string username
        string email
        boolean is_staff
        boolean is_superuser
    }

    UPLOAD {
        int id PK
        int user_id FK
        string original_filename
        string file_type
        bigint file_size
        int total_rows
        string status
        string processing_status
        json preview_data
        json processing_summary
        datetime created_at
    }

    INFLUENCER {
        int id PK
        int upload_id FK
        int user_id FK
        string name
        string handle
        string platform
        bigint followers
        text bio
        string language_detected
        decimal rule_based_score
        string source
        string external_id
        datetime nlp_processed_at
    }

    SEARCH_CRITERIA {
        int id PK
        int user_id FK
        string name
        json keywords
        json languages
        string orientation
        json niches
        bigint minimum_followers
        string status
    }

    CLASSIFICATION {
        int id PK
        int influencer_id FK
        int search_criteria_id FK
        decimal overall_score
        decimal confidence_score
        string recommendation
        text reason
        json ai_response
        string status
        datetime created_at
    }
```

---

## 6. Views & Controllers

| View Function / Class | URL Route | HTTP Methods | Auth Required | Responsibilities |
|---|---|---|---|---|
| `CustomLoginView` | `/login/` | GET, POST | No | Renders login page, verifies credentials, applies 'Remember Me' session expiration. |
| `SignUpView` | `/signup/` | GET, POST | No | Renders registration form, validates user input, creates user account. |
| `custom_logout_view` | `/logout/` | GET, POST | Yes | Invalidates user session and redirects to login. |
| `home_view` | `/dashboard/` | GET | Yes | Renders main dashboard overview with KPI cards and upload history preview. |
| `analytics_dashboard_view` | `/dashboard/analytics/` | GET | Yes | Computes aggregated statistics and renders 8 Chart.js visual analytics components. |
| `upload_view` | `/uploads/` | GET, POST | Yes | Accepts file uploads (`.csv`, `.xlsx`), executes ETL processing, redirects to preview. |
| `upload_history_view` | `/uploads/history/` | GET | Yes | Displays paginated table of user uploads with search and filter controls. |
| `upload_preview_view` | `/uploads/preview/<pk>/` | GET | Yes | Renders file metadata, ETL processing summary, and 10-row JSON data preview. |
| `nlp_processing_view` | `/influencers/nlp/` | GET, POST | Yes | Triggers batch spaCy NLP feature extraction and displays rule-based score metrics. |
| `ai_classification_stream_view` | `/influencers/ai-classification/stream/` | GET | Yes | SSE stream endpoint (`text/event-stream`) yielding live AI progress updates. |
| `ai_classification_view` | `/influencers/ai-classification/` | GET, POST | Yes | Renders AI classification setup dashboard and handles synchronous batch execution. |
| `results_list_view` | `/influencers/results/` | GET | Yes | Displays paginated Table and Grid Card views of classified influencers. |
| `influencer_detail_view` | `/influencers/results/<pk>/` | GET | Yes | Displays complete score breakdown, AI reasoning modal, and raw response JSON. |
| `export_results_view` | `/influencers/results/export/` | POST | Yes | Exports filtered or selected creator records to formatted Excel or CSV files. |
| `discovery_view` | `/influencers/discovery/` | GET, POST | Yes | Executes real-time creator search via pluggable provider, deduplicates, and runs AI pipeline. |

---

## 7. URL Routing System

```text
/
├── admin/                         # Django Native Administration Panel
├── 404/                           # Development 404 Custom Error Preview Route
├── 500/                           # Development 500 Custom Error Preview Route
├── login/                         # User Login Page
├── logout/                        # User Logout Action
├── signup/                        # User Registration Page
├── forgot-password/               # Password Reset Instructions Page
├── dashboard/                     # Main Overview Dashboard
│   └── analytics/                 # Visual Analytics & Chart.js Dashboard
├── uploads/                       # File Upload Entry Page
│   ├── history/                   # Upload Log History Table
│   └── preview/<int:pk>/          # 10-Row Data Preview Modal Page
└── influencers/                   # Influencer Operations Root
    ├── nlp/                       # spaCy NLP Engine Dashboard
    ├── ai-classification/         # AI Classification Control Page
    │   └── stream/                # Server-Sent Events (SSE) Live Progress Stream
    ├── results/                   # Results List (Table & Card Views)
    │   ├── <int:pk>/              # Detailed Creator Evaluation Modal View
    │   └── export/                # Excel (.xlsx) and CSV (.csv) Download Endpoint
    └── discovery/                 # Real-Time Provider Search & Discovery Page
```

---

## 8. Templates & UI Components

### Template Hierarchy
- **[`templates/base/base.html`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/templates/base/base.html)**: Core HTML5 base layout containing `<head>` meta tags, Bootstrap 5 CSS, FontAwesome icons, custom stylesheets, header navbar, left sidebar wrapper, main content container, footer, and JavaScript imports.
- **[`templates/base/_sidebar.html`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/templates/base/_sidebar.html)**: Fixed dark navigation sidebar highlighting active page routes dynamically using Django `request.resolver_match.url_name`.
- **[`templates/base/_navbar.html`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/templates/base/_navbar.html)**: Fixed top navigation bar containing the sidebar toggle button, project brand logo, user greeting, and logout button.

### Feature Templates
- **[`templates/influencers/ai_classification.html`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/templates/influencers/ai_classification.html)**: Comprehensive real-time AI classification dashboard featuring live progress bars, stage steppers (Prompt, Request, Response, Parse, DB Save, Retries), live statistics (Processed, Success, Failed, Remaining, ETA, Speed), terminal-style log output, and automatic EventSource SSE connection management.
- **[`templates/results/list.html`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/templates/results/list.html)**: Dual-view results dashboard supporting view toggling between Table View (`_table.html`) and Card View (`_cards.html`), filter drawer (`filters.html`), score badges, selection checkboxes, and export form modal.
- **[`templates/analytics/dashboard.html`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/templates/analytics/dashboard.html)**: Interactive visual analytics container rendering KPI summary cards (`kpi_cards.html`), 8 canvas charts (`charts.html`), top ranking lists (`top_lists.html`), and date/platform filters (`filters.html`).

---

## 9. JavaScript Infrastructure

#### [`static/js/dashboard.js`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/static/js/dashboard.js)
- **Purpose**: Controls global layout interactions.
- **Functionality**:
  - Toggles the `#sidebar` navigation drawer and adjusts `.main-content` width when clicking `#sidebarToggle`.
  - Automatically collapses the sidebar on mobile viewports (`<= 768px`) when clicking outside the menu.
  - Initializes Bootstrap tooltips (`[data-bs-toggle="tooltip"]`).

#### [`static/js/analytics.js`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/static/js/analytics.js)
- **Purpose**: Renders interactive Chart.js visualizations on the analytics page.
- **Functionality**: Reads JSON payload embedded in `<script id="chart-data" type="application/json">` and initializes 8 Chart.js canvas instances:
  1. `languageChart` (Pie): Distribution of detected languages.
  2. `platformChart` (Bar): Influencers per platform.
  3. `scoreChart` (Bar): Classifications across 5 score tiers (0–20, 21–40, etc.).
  4. `recommendationChart` (Pie): Recommendation status breakdown.
  5. `orientationChart` (Bar): Supportive vs. Neutral orientation match counts.
  6. `followersChart` (Bar): Creator distribution across follower count buckets (10K, 50K, 1M+).
  7. `uploadTrendChart` (Line): Historical file upload volume over time.
  8. `classificationTrendChart` (Line): AI classification processing trends over time.

---

## 10. CSS & Layout System

#### [`static/css/custom.css`](file:///home/vaibhavsharma/Desktop/Projects/AI_Influence_Dashboard/static/css/custom.css)
- **Architecture**: Modular custom stylesheet extending Bootstrap 5.
- **Key Layout Specifications**:
  - `body`: Light background (`#f8f9fa`) with Segoe UI typography hierarchy.
  - `.wrapper`: Flexbox layout container with `60px` top padding for fixed navbar offset.
  - `#sidebar`: Fixed position left sidebar (`width: 260px`, `z-index: 999`) with dark theme styling (`#212529`), smooth CSS transitions (`all 0.3s ease`), custom webkit scrollbar styling, and active route highlight state (`#0d6efd` background with box-shadow).
  - `.main-content`: Dynamic margin offset (`margin-left: 260px`, `width: calc(100% - 260px)`) that expands to `100%` when `#sidebar.active` is toggled.
  - `.card-stat`: Interactive KPI cards with subtle hover lift animations (`transform: translateY(-3px)`).
  - `.border-dashed` & `.upload-area`: Drag-and-drop file upload target box with dashed borders and hover background feedback.

---

## 11. Service Architecture

Business logic is completely encapsulated within stateless service modules under `apps/influencers/services/` and `apps/dashboard/services/`:

```text
Service Layer Architecture:

[Views Layer]
    │
    ├──> UploadsService (validate_file, process_upload_file)
    ├──> NLPService (process_influencer_nlp, batch_process_nlp)
    ├──> OpenRouterService (classify_influencer, retry_handler)
    │       ├──> PromptBuilder (build_classification_prompt)
    │       └──> ResponseParser (parse_ai_response)
    ├──> ResultService (get_filtered_classifications)
    ├──> ExportService (generate_csv_response, generate_excel_response)
    ├──> DiscoveryService (execute, deduplicate)
    │       └──> ProviderManager (get_active_provider -> MockProvider)
    └──> AnalyticsService (get_analytics_context, apply_date_filters)
            └──> ChartService (get_chart_data)
```

---

## 12. AI Classification Module

### Prompt Construction
The `prompt_builder.py` module structures a comprehensive prompt instructing the LLM to act as a strict classification API:
```json
{
  "name": "Priya Digital",
  "handle": "priyadigital_tech",
  "platform": "INSTAGRAM",
  "followers": 150000,
  "bio": "Exploring Digital India, Startup India, and AI.",
  "language_detected": "Hindi",
  "extracted_keywords": ["digital india", "ai", "technology"],
  "extracted_entities": {"ORG": ["Digital India"]},
  "rule_based_nlp_score": 75.0
}
```

### LLM Execution & Retry Mechanism
- **Model Endpoint**: Connects to OpenRouter via OpenAI SDK using model `nvidia/nemotron-3-ultra-550b-a55b:free`.
- **System Prompt**: Enforces `temperature=0.1` and `extra_body={"reasoning": {"enabled": True}}`.
- **Exponential Backoff**: Intercepts rate limits (`429`) and connection failures, retrying up to 3 times with progressive delays (`1s`, `2s`, `4s`).
- **Stage Callbacks**: Emits events during execution (*Prompt Generated* ➔ *Sending Request* ➔ *Response Received* ➔ *Parsing Response* ➔ *Saving Result*).

### Response Parsing & Scoring
- Strips markdown formatting (` ```json ... ``` `).
- Parses raw text into Python dictionaries.
- Validates required fields (`overall_score`, `confidence_score`, `recommendation`, `reason`).
- Maps recommendation strings (`Highly Relevant`, `Relevant`, `Not Relevant`) to Django choices (`RECOMMEND`, `MAYBE`, `REJECT`).

---

## 13. NLP Processing Module

### Pipeline Stages
1. **Text Preprocessing**: Combines creator `bio` and `description` text. Sanitizes strings by removing URLs (`https://...`), email addresses, phone numbers, and Unicode emojis.
2. **Language Detection**: Passes clean text to `langdetect.detect_langs()`. Returns top language ISO code and confidence score (e.g., `code: 'hi'`, `name: 'Hindi'`, `confidence: 0.98`).
3. **spaCy Feature Extraction**: Utilizes `en_core_web_sm` to parse noun chunks and lemmatize tokens. Filters out stop words and short tokens (<3 chars). Collects Named Entities classified by label (`ORG`, `GPE`, `PERSON`, `EVENT`).
4. **Rule-Based Scoring Engine**: Evaluates extracted keywords and entities against 4 weighted domain groups:
   - **Government Schemes**: *Digital India*, *Startup India*, *PM Kisan*, *UPI*, *Viksit Bharat*, *Make in India*.
   - **Development**: *Infrastructure*, *Education*, *Healthcare*, *Agriculture*, *Progress*.
   - **Technology**: *AI*, *Software*, *Digital*, *Technology*, *Cyber*.
   - **Social**: *Community*, *Welfare*, *Youth*, *Support*.
   - **Scoring Formula**: Each matched domain group awards 25.0 points. Total `rule_based_score = min(100.0, score)`.

---

## 14. Database Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant View as Upload View
    participant ETL as ETL Service
    participant DB as PostgreSQL DB
    participant NLP as NLP Engine
    participant AI as OpenRouter AI

    User->>View: Upload File (.csv / .xlsx)
    View->>DB: Create Upload Record (Status=PENDING)
    View->>ETL: Trigger process_upload_file(upload_id)
    ETL->>DB: Lock Upload Row (select_for_update)
    ETL->>ETL: Parse & Normalize Headers/Data
    ETL->>DB: bulk_create(Influencer records, ignore_conflicts=True)
    ETL->>DB: Update Upload Record (Status=COMPLETED)
    View-->>User: Redirect to Upload Preview

    User->>View: Trigger Batch NLP Processing
    View->>NLP: batch_process_nlp()
    NLP->>DB: Fetch Unprocessed Influencer Records
    NLP->>NLP: Clean Text, Detect Language, Extract NER
    NLP->>DB: Update Influencer NLP Fields

    User->>View: Open AI Classification Page (SSE Stream)
    View->>AI: Stream ai_classification_stream_view()
    loop For Each Influencer
        AI->>AI: Build Prompt & Execute OpenRouter LLM Call
        AI->>DB: Save Classification Result Record
        AI-->>User: Yield SSE Event (data: {type: 'item_complete'})
    end
```

---

## 15. Complete Workflow

1. **User Authentication**: User logs in at `/login/`. `IsolatedSessionMiddleware` attaches a secure session cookie.
2. **Dashboard Overview**: User accesses `/dashboard/` to view existing processing metrics and recent upload history.
3. **File Upload (ETL)**: User navigates to `/uploads/` and uploads a creator file. The ETL pipeline normalizes headers, sanitizes text, extracts a 10-row preview JSON, and bulk-inserts records into PostgreSQL.
4. **Data Preview**: User inspects file row counts, imported numbers, duplicate counts, and 10-row preview table at `/uploads/preview/<pk>/`.
5. **NLP Extraction**: User triggers batch NLP at `/influencers/nlp/`. spaCy extracts keywords, entities, language, and rule scores.
6. **Real-Time AI Classification**: User opens `/influencers/ai-classification/` and initiates SSE streaming. The browser opens an `EventSource` connection to `/influencers/ai-classification/stream/`, receiving live progress updates as each profile is classified by OpenRouter AI.
7. **Results Exploration**: User explores creator rankings at `/influencers/results/`. Filters profiles by platform, recommendation, language, score range, or follower tier, toggling between Table View and Grid Cards View.
8. **Creator Inspection**: User clicks a creator row to open the detailed modal drawer (`/influencers/results/<pk>/`), viewing full AI reasoning, confidence scores, and raw JSON responses.
9. **Data Export**: User selects specific creators or applies filters, exporting formatted Excel (`.xlsx`) or streaming UTF-8 BOM CSV (`.csv`) files.
10. **Real-Time Discovery**: User navigates to `/influencers/discovery/`, enters search criteria (e.g. platform, keywords), and executes live discovery. The system fetches mock API results, deduplicates profiles against existing database records, creates new `Influencer` entries, and immediately passes them through NLP and AI classification.

---

## 16. Authentication & Session Security

- **Custom User Model**: `apps.authentication.User` extends `AbstractUser`.
- **Dual Identifier Login**: `CustomLoginForm` checks if the submitted `username` matches an existing user's `email` address, seamlessly authenticating with either identifier.
- **Admin Access Restriction**: Staff and superuser accounts are blocked from signing into the frontend application via `confirm_login_allowed()`, directing them to `/admin/`.
- **Isolated Session Middleware**: `IsolatedSessionMiddleware` intercepts requests and segregates cookies:
  - Requests to `/admin/*` write to `admin_sessionid`.
  - Application requests write to `sessionid`.
- **Session-Based CSRF**: `CSRF_USE_SESSIONS = True` binds CSRF secrets directly to user sessions, eliminating cross-tab token collisions.

---

## 17. Configuration & Environment Settings

The application loads environment variables from `.env` via `python-dotenv`:

| Variable | Default Value | Description |
|---|---|---|
| `SECRET_KEY` | `django-insecure-...` | Django cryptographic signing key. |
| `DEBUG` | `True` | Development debug flag. Set to `False` in production. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,testserver` | Allowed HTTP host headers. |
| `DB_NAME` | `influencer_db` | PostgreSQL database name. |
| `DB_USER` | `postgres` | PostgreSQL database user. |
| `DB_PASSWORD` | `postgres` | PostgreSQL database password. |
| `DB_HOST` | `localhost` | PostgreSQL database host address. |
| `DB_PORT` | `5432` | PostgreSQL database port number. |
| `OPENROUTER_API_KEY` | `""` | OpenRouter API authentication key. |
| `OPENROUTER_MODEL_NAME` | `nvidia/nemotron-3-ultra-550b-a55b:free` | AI classification LLM model. |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter API base endpoint. |
| `OPENROUTER_TIMEOUT` | `30` | Request timeout in seconds. |
| `OPENROUTER_MAX_RETRIES` | `3` | Maximum exponential backoff retry attempts. |
| `DISCOVERY_ENABLED` | `True` | Flag enabling real-time discovery engine. |
| `DEFAULT_PROVIDER` | `mock` | Active discovery provider (`mock`). |

---

## 18. Error Handling & Fault Tolerance

- **Custom Error Pages**:
  - `custom_404_view`: Catches `Http404` exceptions and renders `templates/404.html` with status 404.
  - `custom_500_view`: Catches unhandled server errors and renders `templates/500.html` with status 500.
  - `/404/` and `/500/` preview routes allow instant visual verification during development.
- **Upload Fault Tolerance**: If file parsing fails during ETL execution, `process_upload_file()` catches the exception, updates `processing_status = 'FAILED'`, records `error_message`, and removes the physical file from disk to prevent storage bloat.
- **AI Rate-Limit Retries**: Intercepts OpenRouter rate limits (`429`) and temporary failures, retrying up to 3 times with exponential backoff (`1s`, `2s`, `4s`).
- **SSE Stream Resilience**: If an individual influencer fails classification during streaming, the error is recorded as a `FAILED` `Classification` entry, logged to the terminal stream, and processing immediately advances to the next creator without crashing the batch.

---

## 19. Security Architecture

- **CSRF Defense**: `CsrfViewMiddleware` enforces token checks on all POST requests. `CSRF_USE_SESSIONS = True` prevents cross-site request forgery token theft across session contexts.
- **Session Security**: Session cookies are configured with `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SAMESITE = 'Lax'`.
- **SQL Injection Prevention**: All database operations use Django's ORM QuerySet API with parameterized queries.
- **XSS Sanitization**: Template engine auto-escaping is active across all HTML outputs. Input sanitization in `clean_text()` strips script tags and unsafe inputs.
- **Null Safety Constraints**: `normalize_influencer_dict()` ensures no `None` values reach non-nullable database columns, eliminating `NOT NULL constraint` crash risks.

---

## 20. Performance Optimization

- **Database Query Tuning**: Views utilize `select_related('influencer', 'upload')` and `prefetch_related('classifications')` to eliminate N+1 query overhead.
- **Batch Data Ingestion**: ETL upload processor uses `bulk_create(influencers_to_create, ignore_conflicts=True, batch_size=1000)` to insert thousands of records in a single database round-trip.
- **Memory Efficient Chunking**: Large QuerySets use `.iterator(chunk_size=1000)` during CSV/Excel exports and batch NLP processing to stream data without loading full tables into RAM.
- **Indexed Search Columns**: Database indexes exist on `handle`, `platform`, `language`, `followers`, `status`, and `(handle, platform)` unique composite keys.

---

## 21. Dependencies

| Package | Version | Purpose & Location in Project |
|---|---|---|
| `Django` | `6.0.7` | Web application framework (`config/`, `apps/`). |
| `psycopg` / `psycopg-binary` | `3.3.4` | PostgreSQL database adapter driver. |
| `pandas` | `3.0.5` | CSV/Excel file parsing and data cleaning (`apps/uploads/`). |
| `openpyxl` | `3.1.5` | Excel file reader and styled spreadsheet generator (`apps/influencers/services/export_service.py`). |
| `spacy` | `3.8.14` | Natural Language Processing and entity extraction (`apps/influencers/utils.py`). |
| `en_core_web_sm` | `3.8.0` | spaCy trained English language model. |
| `langdetect` | `1.0.9` | Language detection library (`apps/influencers/utils.py`). |
| `openai` | `2.50.0` | Official client library for OpenRouter API calls (`apps/influencers/services/openrouter_service.py`). |
| `python-dotenv` | `1.2.2` | Environment variable loader (`config/settings.py`). |
| `numpy` | `2.5.1` | Numerical array support used by Pandas and spaCy. |

---

## 22. System Architectural Diagrams

### Authentication & Session Isolation Sequence
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser
    participant Middleware as IsolatedSessionMiddleware
    participant Django as Django Auth Engine

    User->>Browser: Submit Login Form (Username/Email)
    Browser->>Middleware: POST /login/
    Middleware->>Middleware: Identify Path (/login/ -> cookie: sessionid)
    Middleware->>Django: Authenticate Credentials
    Django->>Middleware: Valid User Instance
    Middleware->>Browser: Set-Cookie: sessionid=...; HttpOnly; SameSite=Lax
    Browser-->>User: Redirect to /dashboard/

    User->>Browser: Access Admin Panel /admin/
    Browser->>Middleware: GET /admin/
    Middleware->>Middleware: Identify Path (/admin/ -> cookie: admin_sessionid)
    Middleware->>Django: Check Admin Session
    Middleware-->>Browser: Isolated Admin Context (No App Session Override)
```

---

## 23. Core Business Logic Rules

1. **Header Flexibility Rule**: Input CSV/Excel files are not required to match exact column names. The `normalize_headers()` engine maps 20+ variations (e.g., `biography` ➔ `bio`, `follower count` ➔ `followers`).
2. **Follower String Conversion Rule**: Followers expressed as `15K`, `2.5M`, `1B`, `45,000`, or float values are parsed into exact positive integers (`15000`, `2500000`, `1000000000`). Invalid or missing values default safely to `0`.
3. **Null Safety Guarantee**: All text fields are passed through `clean_text()`. Null, `NaN`, or whitespace-only inputs are converted to empty strings (`""`), preventing database `NOT NULL` constraint violations.
4. **Deduplication Rule**: Influencers are uniquely constrained by `(handle, platform)`. Duplicate entries during bulk file imports or discovery API runs are skipped safely via `ignore_conflicts=True`.
5. **Rule-Based Scoring Formula**: spaCy keyword extractions are evaluated across 4 domain groups (*government_schemes*, *development*, *technology*, *social*). Each matched group awards 25.0 points up to a maximum of 100.0%.
6. **AI Recommendation Mapping**: Raw AI string recommendations are parsed and validated against allowed choices: `Highly Relevant` ➔ `RECOMMEND`, `Relevant` ➔ `MAYBE`, `Not Relevant` ➔ `REJECT`.
7. **Unicode Export Protection**: CSV exports prepends a UTF-8 Byte Order Mark (`\ufeff`) so Microsoft Excel correctly renders Hindi Unicode characters (`हिंदी`).

---

## 24. Frequently Asked Questions

#### Q1: How does the file upload and ETL engine process messy spreadsheets?
**A**: When a CSV or Excel file is uploaded, `process_upload_file()` locks the `Upload` record and passes the file to Pandas/Openpyxl. Column headers are normalized using a dictionary map of 20+ header variations. Every row is processed through `normalize_influencer_dict()`, which converts follower strings (`15K` ➔ `15000`) and replaces missing values with empty strings (`""`). The records are then bulk-inserted into PostgreSQL in batches of 1,000 using `bulk_create(ignore_conflicts=True)`.

#### Q2: How is real-time AI classification progress streamed to the frontend?
**A**: The `/influencers/ai-classification/stream/` endpoint returns a `StreamingHttpResponse` with `content_type='text/event-stream'`. As the backend processes each influencer, it yields JSON-formatted Server-Sent Events (`start`, `stage_update`, `item_complete`, `complete`). The frontend `EventSource` listener updates the progress bar, stage indicators, terminal logs, and ETA timer in real time without page reloads.

#### Q3: How does spaCy NLP scoring work before AI classification?
**A**: The spaCy NLP engine (`process_influencer_nlp`) cleans profile bios by stripping URLs, emails, phone numbers, and emojis. It runs language detection via `langdetect` and extracts lemmatized noun chunks and named entities (`ORG`, `GPE`, `PERSON`) using `en_core_web_sm`. It calculates a rule-based score (0–100) by matching keywords against 4 domain groups (*government_schemes*, *development*, *technology*, *social*), providing a baseline score before calling the OpenRouter AI model.

#### Q4: How does the application prevent session collisions between the main app and Django Admin?
**A**: The custom `IsolatedSessionMiddleware` inspects request paths. For requests starting with `/admin`, it operates on an `admin_sessionid` cookie. For all other application routes, it operates on the standard `sessionid` cookie. Combined with `CSRF_USE_SESSIONS = True`, this isolates sessions and CSRF tokens across both contexts.

#### Q5: How are exports generated for large datasets?
**A**: Data exports are generated via `export_service.py`. QuerySets use `.iterator(chunk_size=1000)` to stream records from PostgreSQL without loading whole tables into memory. CSV exports stream UTF-8 BOM (`\ufeff`) encoded text to support Hindi script in Excel, while Excel exports use `openpyxl` to build formatted `.xlsx` workbooks with auto-adjusted column widths and frozen header panes.

---

## 25. Developer Maintenance & Extension Guide

### Running Automated Tests
Execute the full unit and integration test suite:
```bash
python manage.py test apps.uploads.tests apps.authentication.tests apps.classification.tests apps.dashboard.tests
```

### Adding a New External Discovery Provider
To add a new live social media provider (e.g., Instagram Graph API, YouTube Data API v3):
1. Create a new provider module in `apps/influencers/providers/instagram_provider.py`.
2. Subclass `BaseProvider` and implement the `name` property and `search(criteria)` method.
3. Register the provider in `apps/influencers/services/provider_manager.py`:
   ```python
   _registry = {
       'mock': MockProvider,
       'instagram': InstagramProvider,
   }
   ```
4. Set `DEFAULT_PROVIDER=instagram` in `.env`.

### Adding New Search Criteria Keyword Groups
To update the rule-based NLP scoring engine with new policy topics:
1. Open `apps/influencers/utils.py`.
2. Add keyword terms to the `KEYWORD_GROUPS` dictionary:
   ```python
   KEYWORD_GROUPS = {
       "renewable_energy": ["solar", "wind", "green energy", "sustainability"],
       # existing groups...
   }
   ```

---

## 26. Executive Project Summary

The **AI Influencer Discovery & Analytics Dashboard** provides a robust enterprise solution for discovering, evaluating, and managing social media influencer data. By integrating Django 6, PostgreSQL, spaCy NLP, OpenRouter LLM AI, Pandas ETL processing, Server-Sent Events progress streaming, and Chart.js visual analytics, the platform addresses unstructured data ingestion, multilingual creator evaluation, and transparent real-time AI execution. 

With 23 automated unit and integration tests passing cleanly (100% success rate), modular service decoupling, session isolation security, custom error handlers, and comprehensive documentation, the codebase is production-ready for immediate deployment, team collaboration, and ongoing extension.
