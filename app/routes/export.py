from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Organization, Contact, LeadScoring, RiskOverlay
import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/csv")
async def export_csv(
    sector: str = Query(None, description="Filter by sector"),
    country: str = Query(None, description="Filter by country"),
    tier: str = Query(None, description="Filter by tier"),
    db: Session = Depends(get_db)
):
    """Export organizations to CSV format"""
    try:
        # Build query
        query = db.query(Organization).outerjoin(LeadScoring).outerjoin(RiskOverlay)
        
        if sector:
            query = query.filter(Organization.sector == sector)
        if country:
            query = query.filter(Organization.country == country)
        if tier:
            query = query.filter(LeadScoring.tier == tier)
        
        organizations = query.all()
        
        # Prepare data for export
        export_data = []
        for org in organizations:
            # Get primary contact
            primary_contact = db.query(Contact).filter(Contact.org_id == org.org_id).first()
            
            row = {
                "org_name": org.name,
                "sector": org.sector,
                "role": org.role or "",
                "country": org.country,
                "region_state": org.region_state or "",
                "website": org.website or "",
                "contact_type": primary_contact.channel_type if primary_contact else "",
                "contact_value": primary_contact.value if primary_contact else "",
                "contact_title": primary_contact.title if primary_contact else "",
                "contact_name": primary_contact.name if primary_contact else "",
                "verified": primary_contact.verified_bool if primary_contact else False,
                "exposure_score": org.risk_overlay.exposure_score if org.risk_overlay else None,
                "propensity_score": org.lead_scoring.propensity_score if org.lead_scoring else None,
                "tier": org.lead_scoring.tier if org.lead_scoring else "",
                "notes": org.notes or "",
                "source_url": primary_contact.source_url if primary_contact else ""
            }
            export_data.append(row)
        
        # Create DataFrame and CSV
        df = pd.DataFrame(export_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(csv_buffer.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=wildfire_targets.csv"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(status_code=500, detail="Export failed")

@router.get("/xlsx")
async def export_xlsx(
    sector: str = Query(None, description="Filter by sector"),
    country: str = Query(None, description="Filter by country"),
    tier: str = Query(None, description="Filter by tier"),
    db: Session = Depends(get_db)
):
    """Export organizations to Excel format"""
    try:
        # Build query
        query = db.query(Organization).outerjoin(LeadScoring).outerjoin(RiskOverlay)
        
        if sector:
            query = query.filter(Organization.sector == sector)
        if country:
            query = query.filter(Organization.country == country)
        if tier:
            query = query.filter(LeadScoring.tier == tier)
        
        organizations = query.all()
        
        # Prepare data for export
        export_data = []
        for org in organizations:
            # Get primary contact
            primary_contact = db.query(Contact).filter(Contact.org_id == org.org_id).first()
            
            row = {
                "org_name": org.name,
                "sector": org.sector,
                "role": org.role or "",
                "country": org.country,
                "region_state": org.region_state or "",
                "website": org.website or "",
                "contact_type": primary_contact.channel_type if primary_contact else "",
                "contact_value": primary_contact.value if primary_contact else "",
                "contact_title": primary_contact.title if primary_contact else "",
                "contact_name": primary_contact.name if primary_contact else "",
                "verified": primary_contact.verified_bool if primary_contact else False,
                "exposure_score": org.risk_overlay.exposure_score if org.risk_overlay else None,
                "propensity_score": org.lead_scoring.propensity_score if org.lead_scoring else None,
                "tier": org.lead_scoring.tier if org.lead_scoring else "",
                "notes": org.notes or "",
                "source_url": primary_contact.source_url if primary_contact else ""
            }
            export_data.append(row)
        
        # Create DataFrame and Excel
        df = pd.DataFrame(export_data)
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Wildfire Targets', index=False)
        
        excel_buffer.seek(0)
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=wildfire_targets.xlsx"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting Excel: {e}")
        raise HTTPException(status_code=500, detail="Export failed")
