from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import Contact, Organization
from app.schemas import ContactResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    org_id: str = None,
    db: Session = Depends(get_db)
):
    """List contacts, optionally filtered by organization"""
    query = db.query(Contact)
    if org_id:
        query = query.filter(Contact.org_id == org_id)
    
    contacts = query.all()
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: str, db: Session = Depends(get_db)):
    """Get contact by ID"""
    contact = db.query(Contact).filter(Contact.contact_id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact
