import argparse
import asyncio
import json
import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import insert, select, text
from sqlalchemy.sql import func

from app.db.models import Video, VideoSnapshot
from app.db.session import session_factory


def _parse_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value)


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _chunked(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _build_video_row(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": _parse_uuid(raw["id"]),
        "creator_id": raw["creator_id"],
        "video_created_at": _parse_dt(raw["video_created_at"]),
        "views_count": int(raw["views_count"]),
        "likes_count": int(raw["likes_count"]),
        "comments_count": int(raw["comments_count"]),
        "reports_count": int(raw["reports_count"]),
        "created_at": _parse_dt(raw["created_at"]),
        "updated_at": _parse_dt(raw["updated_at"]),
    }


def _build_videosnapshot_row(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": _parse_uuid(raw["id"]),
        "video_id": _parse_uuid(raw["video_id"]),
        "views_count": int(raw["views_count"]),
        "likes_count": int(raw["likes_count"]),
        "comments_count": int(raw["comments_count"]),
        "reports_count": int(raw["reports_count"]),
        "delta_views_count": int(raw["delta_views_count"]),
        "delta_likes_count": int(raw["delta_likes_count"]),
        "delta_comments_count": int(raw["delta_comments_count"]),
        "delta_reports_count": int(raw["delta_reports_count"]),
        "created_at": _parse_dt(raw["created_at"]),
        "updated_at": _parse_dt(raw["updated_at"]),
    }


async def load_data(path: Path, batch_size: int, truncate: bool):
    payload = json.loads(path.read_text(encoding="utf-8"))
    videos_raw_from_json = payload.get("videos")
    if not isinstance(videos_raw_from_json, list):
        raise ValueError("Ожидается JSON формата {'videos': {...}")

    video_row: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]] = []

    for video in videos_raw_from_json:
        video_row.append(_build_video_row(video))
        for snap in video.get("snapshots", []):
            snapshot_rows.append(_build_videosnapshot_row(snap))

    async with session_factory() as session:
        async with session.begin():
            if truncate:
                await session.execute(
                    text(
                        "TRUNCATE TABLE video_snapshots, videos RESTART IDENTITY CASCADE"
                    )
                )

            for batch in _chunked(video_row, batch_size):
                await session.execute(insert(Video), batch)

            for batch in _chunked(snapshot_rows, batch_size):
                await session.execute(insert(VideoSnapshot), batch)

        videos_count = await session.scalar(select(func.count()).select_from(Video))
        snapshot_count = await session.scalar(
            select(func.count()).select_from(VideoSnapshot)
        )

        print(f"Загружено в БД videos={videos_count}, snapshots={snapshot_count}")


def _parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    default_path = project_root / "data" / "videos.json"

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=default_path)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--no-truncate", dest="truncate", action="store_false")
    parser.set_defaults(truncate=True)
    return parser.parse_args()


if __name__ == "__main__":
    # python -m scripts.load_data
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    args = _parse_args()
    asyncio.run(
        load_data(path=args.path, batch_size=args.batch_size, truncate=args.truncate)
    )
