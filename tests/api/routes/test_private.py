import uuid

from fastapi.testclient import TestClient
from pymongo.database import Database

from app import crud
from app.core.config import settings


def test_create_user(client: TestClient, db: Database) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/private/users/",
        json={
            "email": "pollo@listo.com",
            "password": "password123",
            "full_name": "Pollo Listo",
        },
    )

    assert r.status_code == 200

    data = r.json()

    user = crud.get_user(db=db, user_id=uuid.UUID(data["id"]))

    assert user
    assert user.email == "pollo@listo.com"
    assert user.full_name == "Pollo Listo"
