from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Organization, LeadScoring, RiskOverlay
from app.routes.review import approve_organization, reject_organization
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Templates
templates = Jinja2Templates(directory="app/ui/templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Admin dashboard showing organizations"""
    # Get organizations with their scoring
    organizations = db.query(Organization).outerjoin(LeadScoring).outerjoin(RiskOverlay).all()
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "organizations": organizations
    })

@router.get("/review", response_class=HTMLResponse)
async def review_queue(request: Request, db: Session = Depends(get_db)):
    """Review queue for pending organizations"""
    pending_orgs = db.query(Organization).join(LeadScoring).filter(
        LeadScoring.reviewer_status == "pending"
    ).all()
    
    return templates.TemplateResponse("review_queue.html", {
        "request": request,
        "organizations": pending_orgs
    })

@router.post("/approve/{org_id}")
async def approve_org_admin(
    org_id: str,
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Approve organization from admin UI"""
    return await approve_organization(org_id, notes, db)

@router.post("/reject/{org_id}")
async def reject_org_admin(
    org_id: str,
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Reject organization from admin UI"""
    return await reject_organization(org_id, notes, db)
