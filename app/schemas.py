from pydantic import BaseModel, AnyUrl, Field
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID

# Base schemas
class ContactBase(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    channel_type: Literal["email", "phone", "url", "linkedin"]
    value: str
    verified_bool: bool = False
    source_url: str

class ProgramBase(BaseModel):
    name: str
    url: Optional[str] = None
    description: Optional[str] = None
    source_url: str

class OrganizationBase(BaseModel):
    name: str
    sector: Literal["Government", "Utilities", "Insurance/Analytics", "Forestry/Timber", 
                    "Agriculture", "Real Estate/Property", "NGO/Conservation", 
                    "Technology/GIS", "Academia/Research", "Other"]
    role: Optional[str] = None
    website: Optional[str] = None
    country: str
    region_state: Optional[str] = None
    size_band: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None

# Create schemas
class ContactCreate(ContactBase):
    pass

class ProgramCreate(ProgramBase):
    pass

class OrganizationCreate(OrganizationBase):
    pass

# Response schemas
class ContactResponse(ContactBase):
    contact_id: UUID
    org_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProgramResponse(ProgramBase):
    program_id: UUID
    org_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class RiskOverlayResponse(BaseModel):
    org_id: UUID
    susceptibility: Optional[float] = None
    ignition: Optional[float] = None
    exposure_score: Optional[float] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LeadScoringResponse(BaseModel):
    org_id: UUID
    propensity_score: float
    tier: Literal["A", "B", "C"]
    rationale: str
    reviewer_status: Literal["pending", "approved", "rejected"]
    reviewer_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrganizationResponse(OrganizationBase):
    org_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    contacts: List[ContactResponse] = []
    programs: List[ProgramResponse] = []
    risk_overlay: Optional[RiskOverlayResponse] = None
    lead_scoring: Optional[LeadScoringResponse] = None
    
    class Config:
        from_attributes = True

# LLM Extraction schemas
class ExtractedContact(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    channel_type: Literal["email", "phone", "url", "linkedin"]
    value: str
    verified_bool: bool = False
    source_url: str

class ExtractedProgram(BaseModel):
    name: str
    url: Optional[str] = None
    description: Optional[str] = None

class ExtractedOrganization(BaseModel):
    name: str
    sector: Literal["Government", "Utilities", "Insurance/Analytics", "Forestry/Timber", 
                    "Agriculture", "Real Estate/Property", "NGO/Conservation", 
                    "Technology/GIS", "Academia/Research", "Other"]
    role: Optional[str] = None
    country: str
    region_state: Optional[str] = None
    website: Optional[str] = None
    programs: List[ExtractedProgram] = []
    contacts: List[ExtractedContact] = []
    notes: Optional[str] = None

# Search and filter schemas
class OrganizationFilter(BaseModel):
    sector: Optional[str] = None
    country: Optional[str] = None
    tier: Optional[Literal["A", "B", "C"]] = None
    reviewer_status: Optional[Literal["pending", "approved", "rejected"]] = None
    has_contacts: Optional[bool] = None
    min_exposure_score: Optional[float] = None
    max_exposure_score: Optional[float] = None

class OrganizationSearch(BaseModel):
    query: Optional[str] = None
    filters: Optional[OrganizationFilter] = None
    limit: int = 100
    offset: int = 0

# Export schemas
class ExportRequest(BaseModel):
    format: Literal["csv", "xlsx"]
    filters: Optional[OrganizationFilter] = None
    include_columns: List[str] = Field(default_factory=lambda: [
        "org_name", "sector", "role", "country", "region_state", "website",
        "contact_type", "contact_value", "contact_title", "contact_name",
        "verified", "exposure_score", "propensity_score", "tier", "notes"
    ])
