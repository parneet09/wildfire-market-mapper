from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Organization, LeadScoring
from app.schemas import OrganizationResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/approve/{org_id}")
async def approve_organization(
    org_id: str,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Approve an organization for inclusion in exports"""
    org = db.query(Organization).filter(Organization.org_id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Update lead scoring status
    lead_scoring = db.query(LeadScoring).filter(LeadScoring.org_id == org_id).first()
    if lead_scoring:
        lead_scoring.reviewer_status = "approved"
        lead_scoring.reviewer_notes = notes
        db.commit()
        logger.info(f"Approved organization: {org.name}")
        return {"message": f"Approved {org.name}", "status": "approved"}
    else:
        raise HTTPException(status_code=400, detail="Organization has no lead scoring")

@router.post("/reject/{org_id}")
async def reject_organization(
    org_id: str,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Reject an organization"""
    org = db.query(Organization).filter(Organization.org_id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Update lead scoring status
    lead_scoring = db.query(LeadScoring).filter(LeadScoring.org_id == org_id).first()
    if lead_scoring:
        lead_scoring.reviewer_status = "rejected"
        lead_scoring.reviewer_notes = notes
        db.commit()
        logger.info(f"Rejected organization: {org.name}")
        return {"message": f"Rejected {org.name}", "status": "rejected"}
    else:
        raise HTTPException(status_code=400, detail="Organization has no lead scoring")

@router.get("/pending", response_model=list[OrganizationResponse])
async def get_pending_reviews(db: Session = Depends(get_db)):
    """Get organizations pending review"""
    pending_orgs = db.query(Organization).join(LeadScoring).filter(
        LeadScoring.reviewer_status == "pending"
    ).all()
    return pending_orgs
