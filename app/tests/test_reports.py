import uuid
from datetime import date, datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.auth.dependencies import CurrentUser
from app.database.session import get_db
from app.models.profile import Profile
from app.models.role import Role
from app.models.school import School
from app.models.campaign import Campaign
from app.models.competitor import Competitor
from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class FakeDB:
    def __init__(self, profiles=None, roles=None, schools=None, campaigns=None, competitors=None):
        self.profiles = profiles or {}
        self.roles = roles or {}
        self.schools = schools or {}
        self.campaigns = campaigns or {}
        self.competitors = competitors or {}

    def get(self, model, key):
        if model is Profile:
            return self.profiles.get(key)
        if model is Role:
            return self.roles.get(key)
        if model is School:
            return self.schools.get(key)
        return None

    def query(self, model):
        return FakeQuery(model, self)


class FakeQuery:
    def __init__(self, model, db):
        self.model = model
        self.db = db
        self.filters = []
        self._result_cache = None

    def filter(self, *conditions):
        # Simplified filter tracking - just accept any number of conditions
        for condition in conditions:
            self.filters.append(condition)
        return self

    def first(self):
        if self.model is School:
            # Return first school from db
            for school_id, school in self.db.schools.items():
                return school
        return None

    def all(self):
        if self.model is Campaign:
            return list(self.db.campaigns.values())
        if self.model is Competitor:
            return list(self.db.competitors.values())
        return []


def _override_auth(monkeypatch, *, school_id: uuid.UUID | None, role_name: str):
    profile_id = uuid.uuid4()
    profile = Profile(
        id=profile_id,
        school_id=school_id,
        role_id=uuid.uuid4(),
        full_name="Test User",
        is_active=True,
    )
    role = Role(id=profile.role_id, name=role_name, permissions={})

    school = None
    if school_id:
        school = School(
            id=school_id,
            name="Test School",
            type="school",
            subscription_tier="starter",
            is_active=True,
        )

    fake_db = FakeDB(profiles={profile_id: profile}, roles={profile.role_id: role}, schools={school_id: school} if school else {})

    monkeypatch.setattr("app.auth.dependencies.decode_supabase_jwt", lambda token: {"sub": str(profile_id)})

    def override_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = override_get_db

    return profile, fake_db


def test_reports_csv_requires_authentication(client, monkeypatch):
    response = client.get("/api/v1/reports/csv")
    assert response.status_code == 401


def test_reports_csv_requires_school_link(client, monkeypatch):
    _override_auth(monkeypatch, school_id=None, role_name="viewer")
    response = client.get("/api/v1/reports/csv", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 403


def test_reports_csv_export_empty_school(client, monkeypatch):
    profile, fake_db = _override_auth(monkeypatch, school_id=uuid.uuid4(), role_name="school_admin")

    response = client.get("/api/v1/reports/csv", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Test School" in response.text
    assert "Summary Statistics" in response.text


def test_reports_csv_export_with_campaigns(client, monkeypatch):
    school_id = uuid.uuid4()
    campaign_id = uuid.uuid4()
    profile, fake_db = _override_auth(monkeypatch, school_id=school_id, role_name="school_admin")

    campaign = Campaign(
        id=campaign_id,
        school_id=school_id,
        name="Q1 Campaign",
        channel="email",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 31),
        budget=10000.0,
        spend=7500.0,
        conversions=150,
    )
    fake_db.campaigns[campaign_id] = campaign

    response = client.get("/api/v1/reports/csv", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    assert "Q1 Campaign" in response.text
    assert "email" in response.text


def test_reports_csv_blocks_cross_tenant_access(client, monkeypatch):
    school_id = uuid.uuid4()
    other_school_id = uuid.uuid4()
    profile, fake_db = _override_auth(monkeypatch, school_id=school_id, role_name="school_admin")

    other_school = School(
        id=other_school_id, name="Other School", type="school", subscription_tier="starter", is_active=True
    )
    fake_db.schools[other_school_id] = other_school

    response = client.get(
        f"/api/v1/reports/csv?school_id={other_school_id}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 403


def test_reports_csv_super_admin_can_export_any_school(client, monkeypatch):
    school_id = uuid.uuid4()
    profile, fake_db = _override_auth(monkeypatch, school_id=school_id, role_name="super_admin")

    other_school_id = uuid.uuid4()
    other_school = School(
        id=other_school_id, name="Other School", type="school", subscription_tier="starter", is_active=True
    )
    fake_db.schools[other_school_id] = other_school

    response = client.get(
        f"/api/v1/reports/csv?school_id={other_school_id}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


def test_reports_excel_export(client, monkeypatch):
    school_id = uuid.uuid4()
    profile, fake_db = _override_auth(monkeypatch, school_id=school_id, role_name="school_admin")

    response = client.get("/api/v1/reports/excel", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert response.content[:4] == b"PK\x03\x04"  # ZIP file signature (xlsx is a zip)


def test_reports_pdf_export(client, monkeypatch):
    school_id = uuid.uuid4()
    profile, fake_db = _override_auth(monkeypatch, school_id=school_id, role_name="school_admin")

    response = client.get("/api/v1/reports/pdf", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
    assert response.content[:4] == b"%PDF"


def test_reports_csv_with_date_filtering(client, monkeypatch):
    school_id = uuid.uuid4()
    profile, fake_db = _override_auth(monkeypatch, school_id=school_id, role_name="school_admin")

    response = client.get(
        "/api/v1/reports/csv?start_date=2026-01-01&end_date=2026-03-31",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


def test_reports_filename_attachment_header(client, monkeypatch):
    school_id = uuid.uuid4()
    profile, fake_db = _override_auth(monkeypatch, school_id=school_id, role_name="school_admin")

    response = client.get("/api/v1/reports/csv", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "Test_School" in response.headers.get("content-disposition", "")
    assert ".csv" in response.headers.get("content-disposition", "")
