from fastapi import APIRouter

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/")
async def list_conversations():
    """GET /conversations - Retrieve all conversations for the current user. """
    return []


@router.post("/")
async def create_conversation():
    """POST /conversations - Create or return existing conversation."""
    return {"id": 0, "listing_id": 0, "other_user": {"id": 0, "name": ""}, "created_at": None}


@router.get("/{conversation_id}/messages")
async def list_messages(conversation_id: int):
    """GET /conversations/{id}/messages - Retrieve messages in a conversation."""
    return []


@router.post("/{conversation_id}/messages")
async def send_message(conversation_id: int):
    """POST /conversations/{id}/messages - Send a message."""
    return {"id": 0, "sender_id": 0, "content": "", "created_at": None}
