import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.auth.dependencies import CurrentUser
from app.database.session import get_db
from app.models.profile import Profile
from app.models.role import Role
from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class FakeDB:
    def __init__(self, profile: Profile, role: Role):
        self.profile = profile
        self.role = role

    def get(self, model, key):
        if model is Profile:
            return self.profile if self.profile.id == key else None
        if model is Role:
            return self.role if self.role.id == key else None
        return None


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
    fake_db = FakeDB(profile=profile, role=role)

    monkeypatch.setattr("app.auth.dependencies.decode_supabase_jwt", lambda token: {"sub": str(profile_id)})

    def override_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = override_get_db

    return profile


def test_schools_list_requires_authentication(client, monkeypatch):
    response = client.get("/api/v1/schools/")
    assert response.status_code == 401


def test_campaign_read_rejects_cross_tenant_access(client, monkeypatch):
    profile = _override_auth(monkeypatch, school_id=uuid.uuid4(), role_name="school_admin")
    other_school_id = uuid.uuid4()

    class DummyCampaignService:
        def __init__(self, db):
            self.db = db

        def get(self, _id):
            return SimpleNamespace(id=_id, school_id=other_school_id, name="Other school campaign")

    monkeypatch.setattr("app.api.v1.campaigns.CampaignService", DummyCampaignService)

    response = client.get(
        f"/api/v1/campaigns/{uuid.uuid4()}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 404


def test_viewer_cannot_create_campaign(client, monkeypatch):
    _override_auth(monkeypatch, school_id=uuid.uuid4(), role_name="viewer")

    class DummyCampaignService:
        def __init__(self, db):
            self.db = db

        def create(self, data, school_id=None):
            return SimpleNamespace(id=uuid.uuid4(), school_id=school_id, name=data.name)

    monkeypatch.setattr("app.api.v1.campaigns.CampaignService", DummyCampaignService)

    response = client.post(
        "/api/v1/campaigns/",
        headers={"Authorization": "Bearer test-token"},
        json={"name": "Test campaign", "channel": "email"},
    )
    assert response.status_code == 403
