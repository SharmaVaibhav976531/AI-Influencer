# 📜 Changelog & Version History

All notable changes to the **AI Influencer Discovery & Analytics Dashboard** are documented below.

---

## 🚀 Phase Release Notes

### Phase 1: Project Initialization & Core Framework
- Created modular Django application structure (`authentication`, `dashboard`, `uploads`, `influencers`, `classification`, `analytics`).
- Established base layout templates, top navbar (`_navbar.html`), and custom CSS (`custom.css`).

### Phase 2: Custom Authentication & Session Isolation
- Created custom `User` model inheriting `AbstractUser` with dual Username/Email sign-in support.
- Built `IsolatedSessionMiddleware` separating Django Admin sessions (`admin_sessionid`) from regular user sessions (`sessionid`).
- Set `CSRF_USE_SESSIONS = True` to eliminate CSRF 403 cookie collisions.

### Phase 3: ETL Upload Ingestion & Follower Parser
- Built multi-format upload service supporting `.csv` and `.xlsx` files up to 10MB.
- Created `uploads/utils.py` mapping 20+ header variations (e.g., `follower count` ➔ `followers`).
- Added follower count suffix parser (`150K` ➔ `150,000`) and 10-row JSON preview modal.

### Phase 4: Multilingual spaCy NLP Engine
- Integrated spaCy (`en_core_web_sm`) for Named Entity Recognition (NER) and Noun Chunk extraction.
- Integrated `langdetect` for language identification (*Hindi*, *English*, *Mixed*).
- Created domain rule-based scoring engine across four weighted policy categories.

### Phase 5: OpenRouter AI Classification & SSE Stream UI
- Built `OpenRouterService` connecting via OpenAI Python SDK with exponential backoff retries (`429`).
- Created `ai_classification_stream_view` yielding Server-Sent Events (`text/event-stream`).
- Designed real-time UI progress section with progress bar (`%`), stage stepper, timers, and error feed.

### Phase 6: Results Management, Filtering & Search
- Implemented multi-field filtering (Platform, Language, Recommendation, Score Range, Follower Range).
- Built paginated table and card views with single influencer detail drawers.

### Phase 7: Analytics & Export Engine
- Developed interactive Chart.js visualizations (Doughnut, Bar, Pie, Line charts).
- Built Excel export generator using `openpyxl` with custom header styles and frozen panes.
- Built UTF-8 BOM CSV export (`utf-8-sig`) preserving Hindi script (`हिंदी`) and emojis.

### Phase 8: Pluggable Discovery Architecture
- Implemented `BaseProvider`, `ProviderManager`, and `MockProvider` for creator discovery.
- Added handle+platform deduplication engine (`unique_together = ('handle', 'platform')`).

### Phase 9: Testing & Documentation Overhaul
- Created 21 unit and integration tests across all Django apps.
- Created synthetic QA dataset generators (`Testing/generate_*_qa_data.py`).
- Produced comprehensive repository documentation (`README.md`, `USER_GUIDE.md`, `API_DOCUMENTATION.md`, `DEPLOYMENT_GUIDE.md`, `TESTING_REPORT.md`, `PROJECT_SUMMARY.md`, `PROJECT_WRITEUP.md`).
