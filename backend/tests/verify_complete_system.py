import json
import time
import os
import sys

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

def run_verification():
    client = TestClient(app)
    print("=" * 60)
    print("AgentIQ: Comprehensive End-to-End System Verification")
    print("=" * 60)

    # 1. Root API Check
    print("\n[Check 1] Root API Status & Active Agents")
    res = client.get("/")
    assert res.status_code == 200, f"Root API failed: {res.text}"
    root = res.json()
    print(f"  * Status: {root['status']} ({root['app']} v{root['version']})")
    print(f"  * Total Agents Online: {len(root['agents'])}")
    for a in root['agents']:
        print(f"    - {a}")

    # 2. Direct Profile API (Slide 10)
    print("\n[Check 2] Direct File Profiling Endpoint (/api/v1/profile)")
    sample_path = os.path.join(backend_dir, "sample_data", "Students.csv")
    with open(sample_path, "rb") as f:
        res = client.post("/api/v1/profile", files={"file": ("Students.csv", f, "text/csv")})
    assert res.status_code == 200, f"Direct profiling failed: {res.text}"
    direct_prof = res.json()
    print(f"  * Row Count: {direct_prof['row_count']}, Col Count: {direct_prof['column_count']}")
    print(f"  * Data Quality Score: {direct_prof['quality_score']}/100")
    print(f"  * Sensitive PII Columns Detected: {len(direct_prof['sensitive_columns'])}")
    print(f"  * Profiled Columns: {[c['name'] for c in direct_prof['columns']]}")

    # 3. User Registration & JWT Authentication
    print("\n[Check 3] User Authentication & JWT Generation")
    test_email = f"lead.tester.{int(time.time())}@agentiq.ai"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": test_email,
        "password": "Password123!",
        "full_name": "AgentIQ Lead Tester"
    })
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  * Registered user: {test_email}")
    print(f"  * JWT Bearer Token: {token[:25]}... (valid)")

    # 4. Load Sample Dataset: Students.csv (Slide 12)
    print("\n[Check 4] Sample Dataset Ingestion (Students.csv - Slide 12)")
    load_res = client.post("/api/v1/datasets/load-sample/students", headers=headers)
    assert load_res.status_code == 200, f"Sample load failed: {load_res.text}"
    dataset = load_res.json()
    dataset_id = dataset["id"]
    print(f"  * Ingested Dataset: ID={dataset_id}, Name='{dataset['name']}'")
    print(f"  * Shape: {dataset['row_count']} rows x {dataset['column_count']} columns")

    # 5. Dataset Profile from Catalog
    print("\n[Check 5] Dataset Profile Retrieval")
    prof_res = client.get(f"/api/v1/datasets/{dataset_id}/profile", headers=headers)
    assert prof_res.status_code == 200, f"Profile fetch failed: {prof_res.text}"
    prof = prof_res.json()
    print(f"  * Columns in Schema: {[c['name'] for c in prof['columns']]}")
    print(f"  * Quality Score: {prof['quality_score']}/100")

    # 6. Execute Slide 12 Natural Language Query: "What is average marks by age?"
    print("\n[Check 6] Multi-Agent Pipeline Execution: 'What is average marks by age?'")
    query_start = time.time()
    query_res = client.post("/api/v1/analysis/query", json={
        "dataset_id": dataset_id,
        "question": "What is average marks by age?"
    }, headers=headers)
    duration_ms = round((time.time() - query_start) * 1000, 2)
    assert query_res.status_code == 200, f"Query execution failed: {query_res.text}"
    ans = query_res.json()
    print(f"  * Full Multi-Agent Pipeline Completed in {duration_ms} ms")

    # 7. Agent Trace Observability (Slide 9 & Section 32)
    print("\n[Check 7] Observability Trace Inspection")
    trace = ans.get("trace", ans.get("agent_trace", []))
    print(f"  * Trace Steps Logged: {len(trace)} steps")
    for idx, s in enumerate(trace, 1):
        print(f"    [{idx}] {s.get('agent')}: {s.get('message')} ({s['duration_ms']} ms)")
    assert len(trace) >= 6, "Expected at least 6 agent trace steps"

    # 8. Query Understanding Validation
    print("\n[Check 8] Query Understanding Agent Output")
    schema = ans.get("schema", {})
    intent = schema.get("detected_intent", schema.get("intent"))
    target_cols = schema.get("target_columns", schema.get("measures", []))
    group_by = schema.get("group_by", schema.get("dimensions", []))
    aggregation = schema.get("aggregation", schema.get("aggregations"))
    print(f"  * Extracted Intent: {intent}")
    print(f"  * Measures (Numeric): {target_cols}")
    print(f"  * Dimensions (Categories): {group_by}")
    print(f"  * Aggregation Rule: {aggregation}")
    measures_lower = [m.lower() for m in target_cols]
    dimensions_lower = [d.lower() for d in group_by]
    assert "marks" in measures_lower, "Measure 'marks' not identified"
    assert "age" in dimensions_lower, "Dimension 'age' not identified"

    # 9. Deterministic Pandas Output Validation
    print("\n[Check 9] Deterministic Pandas Tool Execution Results")
    res_data = ans.get("result_data", ans.get("result", {}))
    data_rows = res_data if isinstance(res_data, list) else res_data.get("data", res_data.get("records", []))
    print(f"  * Records Computed: {len(data_rows)}")
    for row in data_rows:
        age_val = row.get("age", row.get("Age"))
        marks_val = row.get("marks", row.get("Marks", 0))
        print(f"    - Age {age_val}: Average Marks = {float(marks_val):.2f}")
    assert len(data_rows) > 0, "No analysis data returned"

    # 10. Multi-Dashboard Alternatives (Slide 12)
    print("\n[Check 10] Multi-Dashboard Alternative Layouts")
    dashboards_bundle = ans.get("dashboards", {})
    designs = dashboards_bundle.get("designs", []) if isinstance(dashboards_bundle, dict) else dashboards_bundle
    print(f"  * Dashboards Generated: {len(designs)}")
    for d in designs:
        print(f"    - Design: '{d.get('name')}'")
        for comp in d.get("components", []):
            print(f"      * Type: {comp.get('type')}, Title: '{comp.get('title')}'")
    assert len(designs) >= 2, "Expected at least 2 dashboard alternatives"

    # 11. Explanation Agent Insights
    print("\n[Check 11] Explanation Agent Grounded Insights")
    exp = ans.get("explanation", {})
    summary_text = exp.get("summary", exp.get("short_answer", ""))
    print(f"  * Summary: {summary_text}")
    print(f"  * Key Insights:")
    for ins in exp.get("key_insights", []):
        print(f"    - {ins}")
    assert summary_text, "Missing explanation summary"

    # 12. Dynamic Question Suggestions
    print("\n[Check 12] Dynamic Question Suggestions")
    sug_res = client.get(f"/api/v1/analysis/suggested-questions/{dataset_id}", headers=headers)
    assert sug_res.status_code == 200, f"Suggestions failed: {sug_res.text}"
    raw_sug = sug_res.json()
    suggestions = raw_sug if isinstance(raw_sug, list) else raw_sug.get("suggested_questions", [])
    print(f"  * Generated Suggestions ({len(suggestions)}):")
    for sq in suggestions:
        print(f"    - {sq}")

    # 13. Data Sources Connector Status (7 Sources)
    print("\n[Check 13] 7 Universal Data Source Connectors")
    ds_res = client.get("/api/v1/data-sources", headers=headers)
    assert ds_res.status_code == 200, f"Data sources failed: {ds_res.text}"
    connectors = ds_res.json()
    print(f"  * Connectors Registered: {len(connectors)}")
    for c in connectors:
        print(f"    - {c['name']} ({c['category']}) -> {c['status']}")
    assert len(connectors) == 7, "Expected 7 data source connectors"

    # 14. ReportLab PDF Export
    print("\n[Check 14] ReportLab PDF Generation")
    export_payload = {
        "title": "AgentIQ Analysis Report: Average Marks by Age",
        "dataset_name": dataset["name"],
        "query": "What is average marks by age?",
        "summary": summary_text,
        "insights": exp.get("key_insights", []),
        "table_headers": ["Age", "Average Marks"],
        "table_rows": [[str(r.get("age", r.get("Age"))), f"{float(r.get('marks', r.get('Marks', 0))):.2f}"] for r in data_rows]
    }
    pdf_res = client.post("/api/v1/export/pdf", json=export_payload, headers=headers)
    assert pdf_res.status_code == 200, f"PDF export failed: {pdf_res.text}"
    pdf_bytes = pdf_res.content
    print(f"  * Generated Valid PDF: {len(pdf_bytes)} bytes")
    assert pdf_bytes.startswith(b"%PDF"), "Response is not a valid PDF file"

    print("\n" + "=" * 60)
    print("ALL 14 END-TO-END VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
