import uuid
from typing import Any

from pymongo import DESCENDING
from pymongo.database import Database

from app.core.security import get_password_hash, verify_password
from app.models import (
    get_datetime_utc,
    Item,
    ItemCreate,
    ItemUpdate,
    User,
    UserCreate,
    UserUpdate,
)


def _user_to_doc(user: User) -> dict[str, Any]:
    doc = user.model_dump(mode="json")
    doc["_id"] = doc.pop("id")
    return doc


def _user_from_doc(doc: dict[str, Any] | None) -> User | None:
    if doc is None:
        return None
    doc = dict(doc)
    doc["id"] = doc.pop("_id")
    return User.model_validate(doc)


def _item_to_doc(item: Item) -> dict[str, Any]:
    doc = item.model_dump(mode="json")
    doc["_id"] = doc.pop("id")
    return doc


def _item_from_doc(doc: dict[str, Any] | None) -> Item | None:
    if doc is None:
        return None
    doc = dict(doc)
    doc["id"] = doc.pop("_id")
    return Item.model_validate(doc)


def create_user(*, db: Database, user_create: UserCreate) -> User:
    user = User(
        email=user_create.email,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
        full_name=user_create.full_name,
        hashed_password=get_password_hash(user_create.password),
    )
    return add_user(db=db, user=user)


def add_user(*, db: Database, user: User) -> User:
    db["users"].insert_one(_user_to_doc(user))
    return user


def get_user(*, db: Database, user_id: uuid.UUID) -> User | None:
    return _user_from_doc(db["users"].find_one({"_id": str(user_id)}))


def get_user_by_email(*, db: Database, email: str) -> User | None:
    return _user_from_doc(db["users"].find_one({"email": email}))


def get_users(
    *, db: Database, skip: int = 0, limit: int = 100
) -> tuple[list[User], int]:
    count = db["users"].count_documents({})
    docs = (
        db["users"]
        .find({})
        .sort("created_at", DESCENDING)
        .skip(skip)
        .limit(limit)
    )
    users = [_user_from_doc(doc) for doc in docs]
    return [user for user in users if user is not None], count


def update_user(*, db: Database, db_user: User, user_in: UserUpdate) -> Any:
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(
            update_data.pop("password")
        )
    updated_user = db_user.model_copy(update=update_data)
    db["users"].replace_one({"_id": str(db_user.id)}, _user_to_doc(updated_user))
    return updated_user


def delete_user(*, db: Database, user_id: uuid.UUID) -> None:
    # MongoDB has no cascade deletes: remove the user's items explicitly
    db["items"].delete_many({"owner_id": str(user_id)})
    db["users"].delete_one({"_id": str(user_id)})


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, db: Database, email: str, password: str) -> User | None:
    db_user = get_user_by_email(db=db, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        db["users"].update_one(
            {"_id": str(db_user.id)},
            {"$set": {"hashed_password": updated_password_hash}},
        )
    return db_user


def create_item(*, db: Database, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    item = Item(
        title=item_in.title,
        description=item_in.description,
        owner_id=owner_id,
        created_at=get_datetime_utc(),
    )
    db["items"].insert_one(_item_to_doc(item))
    return item


def get_item(*, db: Database, item_id: uuid.UUID) -> Item | None:
    return _item_from_doc(db["items"].find_one({"_id": str(item_id)}))


def get_items(
    *,
    db: Database,
    owner_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Item], int]:
    query: dict[str, Any] = {}
    if owner_id is not None:
        query["owner_id"] = str(owner_id)
    count = db["items"].count_documents(query)
    docs = (
        db["items"]
        .find(query)
        .sort("created_at", DESCENDING)
        .skip(skip)
        .limit(limit)
    )
    items = [_item_from_doc(doc) for doc in docs]
    return [item for item in items if item is not None], count


def update_item(*, db: Database, db_item: Item, item_in: ItemUpdate) -> Any:
    update_data = item_in.model_dump(exclude_unset=True)
    updated_item = db_item.model_copy(update=update_data)
    db["items"].replace_one({"_id": str(db_item.id)}, _item_to_doc(updated_item))
    return updated_item


def delete_item(*, db: Database, item_id: uuid.UUID) -> None:
    db["items"].delete_one({"_id": str(item_id)})
