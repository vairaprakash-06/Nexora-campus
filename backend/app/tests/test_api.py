def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "optimisation_engine" in data

def test_dashboard_endpoint(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_rooms"] >= 10
    assert "ai_mode" in data

def test_resources_list(client):
    response = client.get("/api/resources")
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) >= 10
    # Check that AI-LAB-01 exists
    codes = [r["code"] for r in rooms]
    assert "AI-LAB-01" in codes
    assert "AI-LAB-02" in codes

def test_schedules_list(client):
    response = client.get("/api/schedules")
    assert response.status_code == 200
    schedules = response.json()
    assert len(schedules) >= 5

def test_schedule_filters(client):
    response = client.get("/api/schedules/filters")
    assert response.status_code == 200
    filters = response.json()
    assert "departments" in filters
    assert "rooms" in filters
    assert "days" in filters

def test_agents_status(client):
    response = client.get("/api/agents/status")
    assert response.status_code == 200
    data = response.json()
    assert data["total_agents"] == 7
    agent_names = [a["name"] for a in data["agents"]]
    assert "Campus Supervisor Agent" in agent_names
    assert "Optimisation Agent" in agent_names
    assert "Validation and Compliance Agent" in agent_names

def test_analytics(client):
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "room_utilization_by_type" in data
    assert "recovery_statistics" in data

def test_audit_logs(client):
    response = client.get("/api/audit-logs")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
