# 📖 User Guide: AI Influencer Discovery & Analytics Dashboard

Welcome to the **AI Influencer Discovery & Analytics Dashboard**! This step-by-step guide explains how to use all features of the application—from signing in and uploading datasets to running NLP processing, AI classification, viewing analytics, exporting reports, and discovering new creators.

---

## 📌 Table of Contents
1. [Logging In](#1-logging-in)
2. [Navigating the Dashboard](#2-navigating-the-dashboard)
3. [Uploading CSV / Excel Datasets](#3-uploading-csv--excel-datasets)
4. [Previewing Ingested Data](#4-previewing-ingested-data)
5. [Running NLP Processing](#5-running-nlp-processing)
6. [Executing AI Classification](#6-executing-ai-classification)
7. [Exploring Classification Results](#7-exploring-classification-results)
8. [Filtering & Searching Creators](#8-filtering--searching-creators)
9. [Using Analytics Visualizations](#9-using-analytics-visualizations)
10. [Exporting Reports](#10-exporting-reports)
11. [Running Real-Time Discovery](#11-running-real-time-discovery)
12. [Logging Out](#12-logging-out)

---

## 🔑 1. Logging In
1. Open your browser and navigate to `http://127.0.0.1:8000/login/`.
2. Enter your **Username** or **Email Address** and your password.
3. Check **Remember Me** to maintain your active session.
4. Click **Sign In**.

![Login UI Placeholder](https://via.placeholder.com/700x350.png?text=Login+Screen)

---

## 📊 2. Navigating the Dashboard
Once signed in, you will land on the **Dashboard Home** (`/dashboard/`).
- **Top KPI Cards**: View total influencers, NLP processed counts, classified records, and average scores.
- **Sidebar Menu**: Access Uploads, NLP Engine, AI Classification, Results, Analytics, Export, and Discovery.
- **Top Navbar**: Toggle sidebar visibility or manage user settings and logout.

---

## 📁 3. Uploading CSV / Excel Datasets
1. Click **Upload Files** in the sidebar.
2. Drag and drop your `.csv` or `.xlsx` file into the upload drop zone (up to 10MB).
3. Click **Upload & Process File**.
4. The ETL engine automatically cleans text, normalizes column headers (e.g., `biography` ➔ `bio`), and parses follower count suffixes (`150K` ➔ `150,000`).

![Upload UI Placeholder](https://via.placeholder.com/700x350.png?text=Upload+Files+Portal)

---

## 👁️ 4. Previewing Ingested Data
1. Navigate to **Upload History** (`/uploads/history/`).
2. Locate your uploaded file in the audit table.
3. Click **Preview Data**.
4. An interactive modal displays a 10-row JSON preview of normalized creator records.

---

## 🧠 5. Running NLP Processing
1. Click **NLP Engine** in the sidebar.
2. Review the pending influencer count ready for language detection and keyword extraction.
3. Click **Start Batch NLP Processing**.
4. The system detects languages (*Hindi*, *English*, *Mixed*), extracts spaCy entities, and calculates rule-based domain scores.

---

## 🤖 6. Executing AI Classification
1. Click **AI Classification** in the sidebar.
2. Click **Start AI Classification**.
3. A real-time Server-Sent Events (SSE) progress dashboard opens:
   - **Progress Bar**: Shows completion percentage (`24.59%`).
   - **Stage Stepper**: Highlights pipeline steps (`Generating Prompt` ➔ `Sending Request` ➔ `Waiting for AI` ➔ `Parsing Response` ➔ `Saving Result`).
   - **Live Metrics**: Displays processed count, success/failed counters, elapsed timer, and ETA estimate.
   - **Error Activity Feed**: Displays retries and API status codes (`429`).
4. Once completed, click **View Results**.

![AI Classification Stream Placeholder](https://via.placeholder.com/700x350.png?text=Real-Time+SSE+Progress+UI)

---

## 🔍 7. Exploring Classification Results
1. Click **Classification Results** in the sidebar.
2. View creator records in a paginated table or card layout.
3. Click **View Details** on any record to inspect creator bios, overall scores, confidence ratings, AI reasoning, matched keywords, and summary recommendations (`RECOMMEND`, `MAYBE`, `REJECT`).

---

## 🔎 8. Filtering & Searching Creators
Use the top filter bar on the Results page:
- **Search Bar**: Search by handle, creator name, or bio keywords.
- **Platform Filter**: Filter by Instagram, YouTube, Twitter, LinkedIn, or Facebook.
- **Recommendation Filter**: Filter by `RECOMMEND`, `MAYBE`, or `REJECT`.
- **Score & Follower Sliders**: Set minimum and maximum overall score or follower boundaries.

---

## 📈 9. Using Analytics Visualizations
1. Click **Analytics** in the sidebar.
2. Inspect interactive Chart.js visualizations:
   - **Language Split**: Doughnut chart of content languages.
   - **Platform Breakdown**: Bar chart of creator volume per network.
   - **Score Distribution**: Overall score bucket histogram.
   - **Recommendation Breakdown**: Pie chart of AI recommendations.

---

## 📤 10. Exporting Reports
1. Click **Export Data** in the sidebar.
2. Choose your preferred format:
   - **Excel Workbook (`.xlsx`)**: Styled columns, bold headers, frozen top row.
   - **UTF-8 BOM CSV (`.csv`)**: Compatible with Excel, preserving Hindi script (`हिंदी`) and emojis.
3. Click **Download Export File**.

---

## 🌐 11. Running Real-Time Discovery
1. Click **Influencer Discovery** in the sidebar.
2. Enter search keywords (e.g., *Digital India*, *UPI*, *Technology*) and select a target platform.
3. Click **Discover Influencers**.
4. The system queries the provider engine, automatically skipping duplicate creators (`handle` + `platform`).

---

## 🚪 12. Logging Out
Click your username in the top navbar and select **Logout**.
