from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.repository.message_service import create_message, get_messages_by_conversation
from app.models.user import User
from app.routes.users import get_current_user
from app.schemas.message import Message, MessageCreate, MessageSend

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _http_from_repo(exc: ResourceNotFoundError | PermissionDeniedError) -> HTTPException:
    if isinstance(exc, PermissionDeniedError):
        return HTTPException(status_code=403, detail=exc.detail)
    return HTTPException(status_code=404, detail=exc.detail)


@router.get("/")
async def list_conversations():
    """GET /conversations - Retrieve all conversations for the current user. """
    return []


@router.post("/")
async def create_conversation():
    """POST /conversations - Create or return existing conversation."""
    return {"id": 0, "listing_id": 0, "other_user": {"id": 0, "name": ""}, "created_at": None}


@router.get("/{conversation_id}/messages", response_model=list[Message])
async def list_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """GET /conversations/{id}/messages - Retrieve messages in a conversation."""
    try:
        return get_messages_by_conversation(
            db,
            conversation_id,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
        )
    except (ResourceNotFoundError, PermissionDeniedError) as e:
        raise _http_from_repo(e) from e


@router.post(
    "/{conversation_id}/messages",
    response_model=Message,
    status_code=201,
)
async def send_message(
    conversation_id: int,
    payload: MessageSend,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """POST /conversations/{id}/messages - Send a message."""
    body = MessageCreate(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=payload.content,
    )
    try:
        return create_message(db, body)
    except (ResourceNotFoundError, PermissionDeniedError) as e:
        raise _http_from_repo(e) from e
