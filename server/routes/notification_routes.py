import json

from fastapi import APIRouter, Depends, HTTPException

from server.database import get_db_connection
from server.time_utils import utc_timestamp
from server.utils import get_current_user


router = APIRouter(prefix="/api/notifications", tags=["Notification Routes"])


def _serialize_notification(row: dict) -> dict:
    item = {
        "id": row["id"],
        "type": row["type"],
        "message": row["message"],
        "link": row.get("link") or "/home",
        "is_read": bool(row.get("is_read")),
        "created_at": utc_timestamp(row.get("created_at")),
    }
    raw_data = row.get("data")
    if raw_data:
        try:
            item["data"] = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
        except (TypeError, json.JSONDecodeError):
            item["data"] = {}
    return item


@router.get("")
async def get_notifications(user: dict = Depends(get_current_user)):
    """Return persisted notifications with a durable read state."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM notifications WHERE user_id = ? AND is_deleted = 0 ORDER BY created_at DESC, id DESC LIMIT 50",
        (user["id"],),
    )
    rows = cursor.fetchall()
    conn.close()
    return [_serialize_notification(dict(row)) for row in rows]


@router.patch("/{notification_id}/read")
async def mark_notification_read(notification_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ? AND is_deleted = 0",
        (notification_id, user["id"]),
    )
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Notification not found")
    conn.commit()
    conn.close()
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_notifications_read(user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0 AND is_deleted = 0",
        (user["id"],),
    )
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return {"updated": updated}


@router.delete("/read")
async def delete_read_notifications(user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notifications SET is_deleted = 1 WHERE user_id = ? AND is_read = 1 AND is_deleted = 0",
            (user["id"],),
        )
        deleted = cursor.rowcount
        conn.commit()
        return {"deleted": deleted}
    finally:
        conn.close()


@router.delete("/{notification_id}")
async def delete_notification(notification_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notifications SET is_deleted = 1 WHERE id = ? AND user_id = ? AND is_deleted = 0",
        (notification_id, user["id"]),
    )
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Notification not found")
    conn.commit()
    conn.close()
    return {"message": "Notification deleted"}
