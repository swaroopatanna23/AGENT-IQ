# AgentIQ: An AI Framework for Universal File Analysis and Interactive Dashboard Generation over Data

**Major Project** | **Department of Data Engineering** | **CSE-Data Science**  
**Regulation:** R23 | **Course Code:** R23MSCSP003 | **Batch Number:** 08  

### Project Team (Batch 08)
- **Tanna Swaroopa** (23331A4461)
- **Chevvuri Devi Amrutha** (23331A4409)
- **Sakala Yezna Priya** (23331A4451)
- **Pentapati Ratna Sravani** (23331A4443)

**Guide:** Mr. M. Aswini Kumar, Assistant Professor  
**Project Coordinator:** Dr. P. Srinivasa Rao, Professor  
**Head of the Department:** Dr. V. Jyothi, Associate Professor  

---

## 1. Abstract
**AgentIQ** is an academic, production-grade multi-agent AI framework for automated universal file analysis and interactive dashboard generation. It unifies the end-to-end data intelligence lifecycle: data understanding, natural language query understanding, adaptive workflow planning, deterministic analytical execution, privacy preservation, automated visualization selection, and explainable insight generation. The system operates across heterogeneous data sources (CSV, Excel, JSON, Google Sheets, MySQL, PostgreSQL, and MongoDB) with multilingual query capabilities and real-time agent execution observability.

---

## 2. System Architecture & Methodology

```
USER
 ↓
DATA SOURCES (CSV, Excel, JSON, Google Sheets, Relational DBs, NoSQL)
 ↓
DATA AGENT (Deterministic Pandas Profiling & Quality Scoring)
 ↓
QUERY UNDERSTANDING AGENT (Gemini 2.5 + TF-IDF/SVM Baseline)
 ↓
ANALYSIS SCHEMA (Pydantic Intermediate Representation)
 ↓
PLANNING AGENT (Step-by-Step Execution Formulation)
 ↓
ANALYSIS AGENT (Deterministic Pandas / NumPy Controlled Tools)
 ↓
VALIDATION AND PRIVACY (Integrity Verification & PII Masking)
 ↓
VISUALIZATION AGENT (Automated Chart Selection & Multi-Dashboard Generation)
 ↓
MULTIPLE DASHBOARDS (Design A: Overview, Design B: Breakdown, Design C: Trend)
 ↓
EXPLANATION & REFINEMENT (Grounded Natural Language Insights)
 ↓
FINAL DASHBOARD (Studio Customization & PDF/CSV Export)
```

---

## 3. Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Validation:** Pydantic v2
- **Database ORM:** SQLAlchemy (configured for SQLite local out-of-the-box & PostgreSQL)
- **Analytical Compute Engine:** Pandas, NumPy, SciPy (100% deterministic — zero arbitrary code execution)
- **AI / LLM:** Official Google GenAI SDK (`google-genai` / Gemini 2.5 Flash)
- **Machine Learning Baseline:** Scikit-learn (TF-IDF + LinearSVC intent classifier)
- **Security:** JWT authentication & native Bcrypt password hashing
- **Report Generation:** ReportLab PDF Generation

### Frontend
- **Framework:** React 18 + TypeScript + Vite
- **Styling:** Tailwind CSS + PostCSS
- **Visualization:** Recharts & Chart.js
- **Routing:** React Router v6
- **Icons:** Lucide-react
- **Data Fetching:** Axios + TanStack Query

---

## 4. Multi-Agent System Roles

1. **Data Agent (`DataAgent`)**:
   - Analyzes raw data streams to detect row/column counts, data types (numerical, categorical, datetime, text), missing values, duplicates, and outliers.
   - Scans for PII / sensitive attributes (email, phone, SSN, confidential financials) and computes an overall **Quality Score** (0–100%).
2. **Query Understanding Agent (`QueryUnderstandingAgent`)**:
   - Converts natural language queries into an `AnalysisSchema`.
   - Combines a TF-IDF + LinearSVC baseline intent model with Google Gemini semantic slot-filling.
   - Prevents column hallucination via strict fuzzy matching against actual schema columns.
3. **Planning Agent (`PlanningAgent`)**:
   - Generates an explicit, sequential analytical execution plan for the compute engine, rendered in the UI trace.
4. **Analysis Agent (`AnalysisAgent`)**:
   - Executes deterministic calculations using controlled functions (`filter_data`, `group_and_aggregate`, `sort_data`, `calculate_statistics`, `calculate_correlation`, `calculate_trend`, `distribution_analysis`).
5. **Validation & Privacy Agent (`ValidationPrivacyAgent`)**:
   - Verifies result integrity and masks sensitive attributes before passing data to charts or explanations.
6. **Visualization Agent (`VisualizationAgent`)**:
   - Selects optimal chart types (Bar, Line, Area, Donut, Scatter, KPI Card) and synthesizes 3 interactive dashboard alternatives (Designs A, B, and C).
7. **Explanation Agent (`ExplanationAgent`)**:
   - Produces grounded natural language answers, key insights, and observations strictly referencing verified calculated numbers.

---

## 5. Quick Start Guide

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### Backend Setup
1. Open terminal in `backend/`:
   ```bash
   cd backend
   ```
2. Activate Python environment:
   ```powershell
   # Windows PowerShell
   C:\Users\TIRUPATI\.agentiq_venv\Scripts\Activate.ps1
   ```
3. Run backend server:
   ```bash
   python run.py
   ```
   Backend will be running at: `http://127.0.0.1:8000`  
   Interactive API docs (Swagger): `http://127.0.0.1:8000/docs`

### Frontend Setup
1. Open terminal in `frontend/`:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend will be running at: `http://localhost:5173`

---

## 6. Sample Datasets Included

Ready-to-analyze demo datasets are pre-bundled in `sample_data/`:
1. `Students.csv` / `students_performance.csv` (Education — mirrors Slide 12)
2. `online_retail_sales.csv` (E-Commerce / Sales)
3. `employee_workforce.csv` (Business / HR)
4. `healthcare_patients.csv` (Healthcare / Clinical)

---

## 7. Sample Queries to Test

- *"What is average marks by age?"* (from presentation Slide 12)
- *"Which region has the highest sales?"*
- *"Show the monthly sales trend."*
- *"What are the top 5 products by revenue?"*
- *"Compare salary across departments."*
- *"What is the correlation between attendance and marks?"*
- *"Show the distribution of treatment cost."*

---

## 8. Automated Testing
Run the complete backend test suite:
```bash
pytest backend/tests/test_end_to_end.py -v
```

---

## 9. Academic Review & Attribution
Developed for the final-year Major Project evaluation under Department of Data Engineering, CSE-Data Science, Regulation R23.
