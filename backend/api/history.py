
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database import get_db
from database.models import ChatThread
from utils.auth_middleware import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])

class ThreadCreate(BaseModel):
    messages: List[Dict[str, Any]]
    title: str = "New Conversation"

@router.post("/{email}/{thread_id}")
def save_thread(
    email: str, 
    thread_id: str, 
    thread_data: ThreadCreate, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Save or update a chat thread.
    Requires authentication - user can only save their own threads.
    """
    # Verify authenticated user matches the email in URL
    if current_user != email:
        raise HTTPException(status_code=403, detail="Cannot access another user's threads")
    
    # Check if exists
    existing_thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    
    if existing_thread:
        # Update
        existing_thread.messages = thread_data.messages
        existing_thread.title = thread_data.title
        # Verify email matches
        if existing_thread.user_email != email:
             raise HTTPException(status_code=403, detail="Thread belongs to another user")
    else:
        # Create
        new_thread = ChatThread(
            id=thread_id,
            user_email=email,
            title=thread_data.title,
            messages=thread_data.messages
        )
        db.add(new_thread)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"status": "success", "thread_id": thread_id}

@router.get("/{email}")
def get_user_threads(
    email: str, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get all threads for a user - requires authentication"""
    # Verify authenticated user matches the email in URL
    if current_user != email:
        raise HTTPException(status_code=403, detail="Cannot access another user's threads")
    
    threads = db.query(ChatThread).filter(ChatThread.user_email == email).order_by(ChatThread.created_at.desc()).all()
    return threads

@router.get("/{email}/{thread_id}")
def get_thread(
    email: str, 
    thread_id: str, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get a specific thread - requires authentication"""
    # Verify authenticated user matches the email in URL
    if current_user != email:
        raise HTTPException(status_code=403, detail="Cannot access another user's threads")
    
    thread = db.query(ChatThread).filter(ChatThread.id == thread_id, ChatThread.user_email == email).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread
