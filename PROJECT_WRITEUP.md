# 📝 Technical Assignment Write-Up

## 📌 Assignment Objective
The primary objective of this technical assignment was to design, architect, and implement a full-stack, enterprise-ready **AI Influencer Discovery & Analytics Dashboard** using Django 6 and modern AI/NLP tools. The platform must ingest raw creator data (CSV/Excel), perform automated Natural Language Processing (NLP) for language detection and entity extraction, execute LLM-based AI classification via OpenRouter, visualize analytics interactively, and export presentation-ready reports.

---

## 🎯 Approach & Architectural Design Decisions
1. **Modular Django Architecture**: Organized the application into decoupled, domain-driven Django apps (`authentication`, `dashboard`, `uploads`, `influencers`, `classification`, `analytics`) to maintain clean separation of concerns.
2. **Robust ETL Pipeline**: Standardized raw file ingestion in `apps/uploads/utils.py` by mapping 20+ header variations (e.g., `biography` ➔ `bio`, `followers_count` ➔ `followers`), cleaning control characters (`\x00`), and normalizing numerical strings (`150K`, `3.5M`) into integers before database persistence.
3. **Hybrid AI/NLP Evaluation**:
   - **spaCy NLP**: Utilized `spaCy` (`en_core_web_sm`) and `langdetect` for deterministic language detection, Named Entity Recognition (NER), and domain rule-based scoring (0–100) across policy areas (*Government Schemes*, *Development*, *Technology*, *Social*).
   - **OpenRouter LLM AI Engine**: Used the OpenAI Python SDK to send structured prompts to OpenRouter models (`nvidia/nemotron-3-ultra-550b-a55b:free`), enforcing strict JSON responses containing overall scores, confidence metrics, reasoning, and recommendations (`RECOMMEND`, `MAYBE`, `REJECT`).
4. **Real-Time Streaming UX (SSE)**: Implemented `ai_classification_stream_view` using Django's `StreamingHttpResponse` emitting Server-Sent Events (`text/event-stream`). This streams live progress metrics, stage stepper updates, elapsed timers, and ETA estimates directly to the UI without requiring Redis or Celery worker overhead.

---

## ⚡ Challenges Faced & Solutions Implemented

| Challenge | Root Cause | Solution Implemented |
|---|---|---|
| **CSRF Cookie Collision (403 Error)** | Standard cookie-based CSRF tokens clashed when toggling between Django Admin (`/admin/`) and Application views. | Configured `CSRF_USE_SESSIONS = True` in `settings.py` to store CSRF tokens directly in session state. |
| **Session State Overwrite** | Admin login overwrote the application session cookie `sessionid`. | Implemented custom `IsolatedSessionMiddleware` to assign `admin_sessionid` to `/admin/` routes, completely isolating admin and user sessions. |
| **Database NOT NULL Violations** | Uploaded CSVs containing empty `Bio` or `Description` fields passed `None` to non-nullable database columns. | Created `normalize_influencer_dict` in `uploads/utils.py` to convert `None` and `NaN` values to safe string fallbacks (`""`). |
| **Opaque Long-Running AI Jobs** | Synchronous HTTP POST requests caused the browser loading spinner to freeze without feedback. | Developed a Server-Sent Events (SSE) streaming endpoint delivering live batch progress updates, stage highlights, and terminal execution logs. |
| **Hindi Script Corruption in CSV Export** | Default CSV exports corrupted Hindi script (`हिंदी`) and emojis when opened in Microsoft Excel. | Configured `export_service.py` to emit streaming CSV responses with `utf-8-sig` (UTF-8 BOM) encoding. |

---

## 🏆 Final Result
The system successfully processes, scores, classifies, visualizes, and exports creator datasets. All **21 automated unit and integration tests** pass with a 100% success rate, delivering a polished, production-ready solution suitable for direct deployment and submission.
