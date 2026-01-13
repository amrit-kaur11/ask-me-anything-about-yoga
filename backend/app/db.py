from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv


def _load_env() -> None:
    candidates = [
        os.path.join("backend", "storage", ".env"),
        os.path.join("backend", ".env"),
        ".env",
    ]
    for p in candidates:
        if os.path.exists(p):
            load_dotenv(p, override=False)
            return


@dataclass
class Mongo:
    client: AsyncIOMotorClient
    db: AsyncIOMotorDatabase
    requests_col: Any
    feedback_col: Any


def init_mongo() -> Mongo:
    _load_env()

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.getenv("MONGO_DB", "askme_ai")
    req_col = os.getenv("MONGO_COLLECTION_REQUESTS", "requests")
    fb_col = os.getenv("MONGO_COLLECTION_FEEDBACK", "feedback")

    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]

    return Mongo(
        client=client,
        db=db,
        requests_col=db[req_col],
        feedback_col=db[fb_col],
    )


async def ensure_indexes(mongo: Mongo) -> None:
    await mongo.requests_col.create_index("request_id", unique=True)
    await mongo.requests_col.create_index("created_at")
    await mongo.feedback_col.create_index("request_id")
    await mongo.feedback_col.create_index("created_at")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def log_request(mongo: Mongo, doc: Dict[str, Any]) -> None:
    await mongo.requests_col.insert_one(doc)


async def attach_feedback(
    mongo: Mongo,
    request_id: str,
    rating: str,
    comment: Optional[str] = None,
) -> None:
    feedback_doc = {
        "request_id": request_id,
        "rating": rating,  # "up" | "down"
        "comment": comment,
        "created_at": utc_now(),
    }
    await mongo.feedback_col.insert_one(feedback_doc)

    await mongo.requests_col.update_one(
        {"request_id": request_id},
        {"$set": {"feedback": feedback_doc}},
    )
