# 🔌 API Documentation: Implemented Endpoints

This document details all active HTTP endpoints implemented in the application.

---

## 📋 Endpoint Index

| App | Named Route | Path | HTTP Methods | Auth Required? |
|---|---|---|---|---|
| `authentication` | `login` | `/login/` | `GET`, `POST` | No |
| `authentication` | `logout` | `/logout/` | `GET`, `POST` | Yes |
| `authentication` | `signup` | `/signup/` | `GET`, `POST` | No |
| `dashboard` | `dashboard:home` | `/dashboard/` | `GET` | Yes |
| `dashboard` | `dashboard:analytics` | `/dashboard/analytics/` | `GET` | Yes |
| `uploads` | `uploads:upload` | `/uploads/` | `GET`, `POST` | Yes |
| `uploads` | `uploads:history` | `/uploads/history/` | `GET` | Yes |
| `uploads` | `uploads:preview` | `/uploads/preview/<pk>/` | `GET` | Yes |
| `influencers` | `influencers:nlp_dashboard` | `/influencers/nlp/` | `GET`, `POST` | Yes |
| `influencers` | `influencers:ai_classification` | `/influencers/ai-classification/` | `GET`, `POST` | Yes |
| `influencers` | `influencers:ai_classification_stream` | `/influencers/ai-classification/stream/` | `GET` | Yes |
| `influencers` | `influencers:results_list` | `/influencers/results/` | `GET` | Yes |
| `influencers` | `influencers:influencer_detail` | `/influencers/results/<pk>/` | `GET` | Yes |
| `influencers` | `influencers:export_results` | `/influencers/results/export/` | `GET` | Yes |
| `influencers` | `influencers:discovery` | `/influencers/discovery/` | `GET`, `POST` | Yes |

---

## 🔍 Endpoint Specifications

### 1. Authentication Endpoints

#### `POST /login/`
- **Purpose**: Authenticates a user using username or email.
- **Auth Required**: No
- **Request Parameters (Form Data)**:
  - `username`: String (Username or Email)
  - `password`: String
  - `remember_me`: Checkbox (Optional)
- **Response**: `302 Redirect` to `/dashboard/` on success; `200 OK` with form errors on failure.

#### `GET /logout/`
- **Purpose**: Terminates the current user session.
- **Auth Required**: Yes
- **Response**: `302 Redirect` to `/login/`.

---

### 2. File Upload Endpoints

#### `POST /uploads/`
- **Purpose**: Uploads a CSV or Excel creator file and executes ETL header normalization.
- **Auth Required**: Yes
- **Request Parameters (Multipart Form)**:
  - `file`: Multipart File (`.csv`, `.xlsx`, max 10MB)
- **Response Example**: `302 Redirect` to `/uploads/history/` with success flash message.

#### `GET /uploads/preview/<pk>/`
- **Purpose**: Fetches a 10-row JSON preview of an uploaded dataset.
- **Auth Required**: Yes
- **URL Parameters**: `pk` (Integer - Upload ID)
- **Response Example (`200 OK`)**:
```json
{
  "status": "success",
  "filename": "influencers_batch_1.csv",
  "headers": ["Name", "Handle", "Platform", "Followers", "Bio"],
  "rows": [
    {
      "Name": "Rahul Tech",
      "Handle": "rahul_tech",
      "Platform": "YOUTUBE",
      "Followers": 150000,
      "Bio": "Tech creator discussing Digital India & UPI."
    }
  ]
}
```

---

### 3. AI Classification & Streaming Endpoints

#### `GET /influencers/ai-classification/stream/`
- **Purpose**: Streams real-time Server-Sent Events (SSE) detailing AI classification progress, stage updates, and ETA metrics.
- **Auth Required**: Yes
- **Headers**: `Accept: text/event-stream`
- **Response (`200 OK` Streaming Response)**:
```text
data: {"type": "start", "total_found": 50, "already_classified": 10, "pending_total": 40}

data: {"type": "stage_update", "index": 1, "pending_total": 40, "handle": "rahul_tech", "stage": "Sending Request", "processed": 0, "success": 0, "failed": 0, "remaining": 40}

data: {"type": "item_complete", "index": 1, "pending_total": 40, "handle": "rahul_tech", "processed": 1, "success": 1, "failed": 0, "remaining": 39, "completion_pct": 2.5}

data: {"type": "complete", "pending_total": 40, "processed": 40, "success": 40, "failed": 0, "total_time_str": "01:20", "avg_time_seconds": 2.0}
```

---

### 4. Results & Export Endpoints

#### `GET /influencers/results/`
- **Purpose**: Renders the search, filter, and paginated creator table.
- **Auth Required**: Yes
- **Query Parameters**:
  - `q`: String (Search query)
  - `platform`: String (`INSTAGRAM`, `YOUTUBE`, `TWITTER`, `LINKEDIN`, `FACEBOOK`)
  - `recommendation`: String (`RECOMMEND`, `MAYBE`, `REJECT`)
  - `min_score`: Integer (0–100)
  - `max_score`: Integer (0–100)
- **Response**: `200 OK` (HTML Render)

#### `GET /influencers/results/export/`
- **Purpose**: Exports current filtered classification results to Excel or UTF-8 BOM CSV.
- **Auth Required**: Yes
- **Query Parameters**:
  - `format`: String (`excel` or `csv`, Default: `excel`)
- **Response**: Binary download attachment (`.xlsx` or `.csv`).
