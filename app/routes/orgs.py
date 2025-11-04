from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import Organization, RiskOverlay, LeadScoring
from app.schemas import OrganizationResponse, OrganizationFilter, OrganizationSearch
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sector: Optional[str] = None,
    country: Optional[str] = None,
    tier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List organizations with optional filtering"""
    query = db.query(Organization)
    
    if sector:
        query = query.filter(Organization.sector == sector)
    if country:
        query = query.filter(Organization.country == country)
    if tier:
        query = query.join(LeadScoring).filter(LeadScoring.tier == tier)
    
    organizations = query.offset(skip).limit(limit).all()
    return organizations

@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(org_id: str, db: Session = Depends(get_db)):
    """Get organization by ID"""
    organization = db.query(Organization).filter(Organization.org_id == org_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@router.get("/search/", response_model=List[OrganizationResponse])
async def search_organizations(
    q: str = Query(..., description="Search query"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Search organizations by name or description"""
    query = db.query(Organization).filter(
        Organization.name.ilike(f"%{q}%")
    )
    organizations = query.limit(limit).all()
    return organizations

@router.get("/stats/summary")
async def get_organization_stats(db: Session = Depends(get_db)):
    """Get summary statistics for organizations"""
    total_orgs = db.query(Organization).count()
    
    # Count by sector
    sector_counts = db.query(Organization.sector, db.func.count(Organization.org_id)).group_by(Organization.sector).all()
    
    # Count by tier
    tier_counts = db.query(LeadScoring.tier, db.func.count(LeadScoring.org_id)).group_by(LeadScoring.tier).all()
    
    return {
        "total_organizations": total_orgs,
        "by_sector": dict(sector_counts),
        "by_tier": dict(tier_counts)
    }
