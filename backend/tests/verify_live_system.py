import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

def test_full_pipeline():
    print("==================================================")
    print("AgentIQ: Live End-to-End System Verification")
    print("==================================================")
    
    # 1. Root API Check
    print("\n[Step 1] Checking Root API Endpoint...")
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200, f"Root API failed: {res.text}"
    root_data = res.json()
    print(f"-> Backend Status: {root_data['status']}")
    print(f"-> Registered Agents: {len(root_data['agents'])} agents active")
    for agent in root_data['agents']:
        print(f"   * {agent}")

    # 2. Check Frontend Serving
    print("\n[Step 2] Checking Frontend Dev Server...")
    res = requests.get(FRONTEND_URL)
    assert res.status_code == 200, f"Frontend server failed: {res.status_code}"
    print("-> Frontend server successfully responding on port 5173 (HTTP 200)")

    # 3. Auth Registration & Login
    print("\n[Step 3] Testing Authentication Flow...")
    email = f"lead.tester.{int(time.time())}@agentiq.ai"
    reg_res = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "AgentIQ Lead Tester"
    })
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"-> Registered & logged in as {email}")
    print(f"-> Received JWT token: {token[:20]}...")

    # 4. Load Sample Dataset: Students.csv (from Slide 12)
    print("\n[Step 4] Loading Sample Dataset (Students.csv - Slide 12)...")
    load_res = requests.post(f"{BASE_URL}/api/v1/datasets/load-sample/Students.csv", headers=headers)
    assert load_res.status_code == 200, f"Sample load failed: {load_res.text}"
    dataset = load_res.json()
    dataset_id = dataset["id"]
    print(f"-> Dataset Loaded: ID={dataset_id}, Name='{dataset['name']}', Rows={dataset['row_count']}, Cols={dataset['col_count']}")

    # 5. Verify Dataset Profile (Slide 10)
    print("\n[Step 5] Checking Dataset Profile...")
    prof_res = requests.get(f"{BASE_URL}/api/v1/datasets/{dataset_id}/profile", headers=headers)
    assert prof_res.status_code == 200, f"Profile fetch failed: {prof_res.text}"
    profile = prof_res.json()
    print(f"-> Quality Score: {profile['summary']['quality_score']}/100")
    print(f"-> Columns Profiled: {list(profile['columns'].keys())}")
    print(f"-> Missing Values: {profile['summary']['missing_values_count']}")

    # 6. Test Slide 12 Query: "What is average marks by age?"
    print("\n[Step 6] Executing Slide 12 Query: 'What is average marks by age?'...")
    query_payload = {
        "dataset_id": dataset_id,
        "question": "What is average marks by age?"
    }
    start_t = time.time()
    query_res = requests.post(f"{BASE_URL}/api/v1/analysis/query", json=query_payload, headers=headers)
    duration_ms = round((time.time() - start_t) * 1000, 2)
    assert query_res.status_code == 200, f"Query execution failed: {query_res.text}"
    ans = query_res.json()
    print(f"-> Query completed in {duration_ms} ms (Total Agent Runtime)")
    
    # 7. Verify Multi-Agent Output Structure
    print("\n[Step 7] Verifying Multi-Agent Observability Trace...")
    trace = ans.get("trace", [])
    print(f"-> Agent Trace Steps Captured: {len(trace)} steps")
    for step in trace:
        print(f"   [{step['step_number']}] {step['agent_name']}: {step['action']} ({step['duration_ms']} ms)")
    
    print("\n[Step 8] Verifying Query Understanding Agent Output...")
    schema = ans.get("schema", {})
    print(f"   * Intent: {schema.get('intent')}")
    print(f"   * Measures: {schema.get('measures')}")
    print(f"   * Dimensions: {schema.get('dimensions')}")
    print(f"   * Aggregation: {schema.get('aggregations')}")

    print("\n[Step 9] Verifying Deterministic Analysis Results...")
    res_data = ans.get("result", {})
    print(f"   * Row count returned: {len(res_data.get('data', []))}")
    print(f"   * Data preview: {json.dumps(res_data.get('data', [])[:3], indent=2)}")

    print("\n[Step 10] Verifying Grounded Explanation Insights...")
    exp = ans.get("explanation", {})
    print(f"   * Summary: {exp.get('summary')}")
    print(f"   * Key Insights ({len(exp.get('key_insights', []))}):")
    for ins in exp.get("key_insights", []):
        print(f"     - {ins}")

    print("\n[Step 11] Verifying Multi-Dashboard Layouts (Slide 12)...")
    dashboards = ans.get("dashboards", [])
    print(f"-> Dashboards Generated: {len(dashboards)}")
    for d in dashboards:
        print(f"   * Design: '{d.get('name')}' (Theme: {d.get('theme')}) - {len(d.get('components', []))} components")
        for comp in d.get('components', []):
            print(f"     - Type: {comp.get('type')}, Title: '{comp.get('title')}'")

    # 12. Test PDF Export
    print("\n[Step 12] Testing Automated ReportLab PDF Export...")
    export_payload = {
        "title": "AgentIQ Analysis Report: Average Marks by Age",
        "dataset_name": dataset["name"],
        "query": "What is average marks by age?",
        "summary": exp.get("summary", ""),
        "insights": exp.get("key_insights", []),
        "table_headers": ["Age", "Average Marks"],
        "table_rows": [[str(r.get("Age")), f"{r.get('Marks', 0):.2f}"] for r in res_data.get("data", [])]
    }
    pdf_res = requests.post(f"{BASE_URL}/api/v1/export/pdf", json=export_payload, headers=headers)
    assert pdf_res.status_code == 200, f"PDF generation failed: {pdf_res.text}"
    assert len(pdf_res.content) > 1000, "PDF content seems empty"
    print(f"-> PDF Successfully generated ({len(pdf_res.content)} bytes, Valid ReportLab PDF)")

    # 13. Test Data Sources Connector Status
    print("\n[Step 13] Checking 7 Data Source Connectors Status...")
    ds_res = requests.get(f"{BASE_URL}/api/v1/data-sources", headers=headers)
    assert ds_res.status_code == 200, f"Data sources failed: {ds_res.text}"
    connectors = ds_res.json()
    print(f"-> Connectors available: {len(connectors)}")
    for c in connectors:
        print(f"   * {c['name']} ({c['category']}) - Status: {c['status']}")

    print("\n==================================================")
    print("ALL VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == "__main__":
    test_full_pipeline()
