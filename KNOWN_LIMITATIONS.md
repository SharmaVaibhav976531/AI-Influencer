# 📌 Known Limitations & Trade-offs

This document provides a transparent overview of the technical limitations, constraints, and design trade-offs in the current release.

---

## 🔍 1. Architecture & Execution Constraints

### Synchronous Web Request Execution
- **Current Behavior**: File uploading, spaCy NLP feature extraction, and OpenRouter AI classification run synchronously within the HTTP request thread.
- **Impact**: Batch processing very large files (>50,000 creator records) can lock the web process for several minutes if network latency or rate-limiting occurs.
- **Mitigation**: Implemented `bulk_create` for database writes, QuerySet `.iterator()` streaming, and Server-Sent Events (SSE) streaming for user visibility.

---

## 🤖 2. AI & API Constraints

### OpenRouter Free Tier Rate Limits
- **Current Behavior**: The system uses OpenRouter models (`nvidia/nemotron-3-ultra-550b-a55b:free` or custom LLMs). Free tiers are subject to external rate limits (`HTTP 429 Too Many Requests`).
- **Impact**: Large classification runs may experience brief retry pauses (`1s`, `2s`, `4s`) while backoff mechanisms wait for rate limit windows to clear.
- **Mitigation**: Built-in exponential backoff retries and live UI activity feed detailing retry statuses.

### Language Detection Confidence
- **Current Behavior**: Text language is identified via `langdetect` based on short bio strings.
- **Impact**: Very short bios (e.g., "Creator | DM for Collabs") may occasionally be classified as `English` or `Mixed` due to sparse token length.

---

## 🌐 3. Discovery Engine Constraints

### Mock Provider Engine
- **Current Behavior**: The Discovery module currently utilizes a `MockProvider` generating synthetic creator data.
- **Impact**: Live real-time discovery against official Graph APIs (YouTube Data API v3, Instagram Graph API) requires registering developer credentials.
- **Mitigation**: Built on a modular `BaseProvider` architecture, allowing production Graph API connectors to be dropped in without changing business logic.

---

## 💾 4. File Ingestion Constraints

### File Size Ceiling
- **Current Behavior**: File uploads are capped at 10MB per upload session in `apps/uploads/views.py`.
- **Impact**: Single dataset files exceeding 10MB must be split into multiple smaller uploads.
