from collections.abc import Generator

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

from app import crud
from app.core.config import settings
from app.models import UserCreate

_client: MongoClient = MongoClient(str(settings.MONGO_URL), appname=settings.PROJECT_NAME)


def get_database() -> Database:
    """
    Return the application database.

    Uses the database name from the connection string when present,
    otherwise falls back to the MONGO_DB_NAME setting.
    """
    try:
        return _client.get_default_database()
    except Exception:
        return _client.get_database(settings.MONGO_DB_NAME)


def get_db() -> Generator[Database]:
    db = get_database()
    yield db


def init_db(db: Database) -> None:
    # MongoDB is schemaless: "migrations" are just index creation.
    db["users"].create_index("email", unique=True)
    db["items"].create_index([("owner_id", ASCENDING)])
    db["items"].create_index([("created_at", DESCENDING)])

    user = crud.get_user_by_email(db=db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        crud.create_user(db=db, user_create=user_in)
