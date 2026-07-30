# 🔮 Future Enhancements & Product Roadmap

This document outlines planned future improvements and technical roadmap items for future releases.

---

## 🎯 Proposed Technical Enhancements

### 1. Asynchronous Background Task Queue (Celery + Redis)
- **Goal**: Offload heavy ETL file parsing, spaCy NLP processing, and OpenRouter AI classification jobs from the main Django HTTP process to background workers.
- **Benefits**: Instant file upload feedback, non-blocking background execution, and automatic worker scaling.

### 2. Live Social Media API Connectors
- **Goal**: Integrate official third-party social media APIs:
  - **YouTube Data API v3**: Retrieve live channel subscriber counts, video upload frequency, and engagement metrics.
  - **Instagram Graph API**: Fetch business profile metrics, post impressions, and audience demographics.
  - **Twitter/X API v2**: Stream real-time tweet activity and follower engagement rates.

### 3. Advanced NLP & Multilingual Models
- **Goal**: Upgrade language processing from basic spaCy NER to specialized transformer models (e.g., `indic-bert` or HuggingFace transformers) tailored specifically for regional Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi).

### 4. Role-Based Access Control (RBAC) & Teams
- **Goal**: Implement multi-tenant workspace architecture allowing enterprise communications agencies to manage multiple brand workspaces, assign team roles (*Admin*, *Analyst*, *Viewer*), and share creator shortlists.

### 5. Automated PDF Campaign Report Generation
- **Goal**: Build automated PDF summary generation (`WeasyPrint` / `ReportLab`) to export executive campaign summaries, creator scorecards, and visual analytics charts directly to presentation-ready PDF documents.

### 6. Containerization & CI/CD Pipeline
- **Goal**: Provide production-ready `Dockerfile` and `docker-compose.yml` configurations alongside GitHub Actions CI/CD workflows for automated unit testing and cloud deployment.
