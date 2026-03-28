from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repository.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.schemas.conversation import (
    Conversation,
    ConversationStartRequest,
)
from app.schemas.message import Message, MessageCreate, MessageSend
from app.services.conversation import ConversationService
from app.services.listing import ListingService
from app.services.message import MessageService
from app.services.user import UserService

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _http_from_repo(exc: ResourceNotFoundError | PermissionDeniedError) -> HTTPException:
    if isinstance(exc, PermissionDeniedError):
        return HTTPException(status_code=403, detail=exc.detail)
    return HTTPException(status_code=404, detail=exc.detail)


@router.get("/", response_model=list[Conversation])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all conversations for the current user."""
    return ConversationService.list_for_user(db, current_user.id)


@router.post("/", response_model=Conversation, status_code=201)
async def create_conversation(
    payload: ConversationStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or return an existing conversation for a listing."""
    if payload.other_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot start a conversation with yourself")
    other_user = UserService.get_by_id(db, payload.other_user_id)
    if other_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        ListingService.get_or_raise(db, payload.listing_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.detail) from e
    return ConversationService.get_or_create(
        db, payload.listing_id, current_user.id, payload.other_user_id
    )


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
        return MessageService.list_by_conversation(
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
        return MessageService.create(db, body)
    except (ResourceNotFoundError, PermissionDeniedError) as e:
        raise _http_from_repo(e) from e
