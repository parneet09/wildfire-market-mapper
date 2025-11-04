from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    org_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False, index=True)
    sector = Column(String(100), nullable=False, index=True)
    role = Column(String(200), nullable=True)
    website = Column(String(500), nullable=True)
    country = Column(String(100), nullable=False, index=True)
    region_state = Column(String(100), nullable=True, index=True)
    size_band = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    geom = Column(String(100), nullable=True)  # Simplified for now
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contacts = relationship("Contact", back_populates="organization", cascade="all, delete-orphan")
    programs = relationship("Program", back_populates="organization", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="organization", cascade="all, delete-orphan")
    risk_overlay = relationship("RiskOverlay", back_populates="organization", uselist=False, cascade="all, delete-orphan")
    lead_scoring = relationship("LeadScoring", back_populates="organization", uselist=False, cascade="all, delete-orphan")

class Contact(Base):
    __tablename__ = "contacts"
    
    contact_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    name = Column(String(200), nullable=True)
    title = Column(String(200), nullable=True)
    channel_type = Column(Enum("email", "phone", "url", "linkedin", name="channel_type_enum"), nullable=False)
    value = Column(String(500), nullable=False)
    verified_bool = Column(Boolean, default=False)
    source_url = Column(String(1000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="contacts")

class Program(Base):
    __tablename__ = "programs"
    
    program_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    name = Column(String(300), nullable=False)
    url = Column(String(1000), nullable=True)
    description = Column(Text, nullable=True)
    source_url = Column(String(1000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="programs")

class RiskOverlay(Base):
    __tablename__ = "risk_overlay"
    
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), primary_key=True)
    susceptibility = Column(Float, nullable=True)
    ignition = Column(Float, nullable=True)
    exposure_score = Column(Float, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="risk_overlay")

class Source(Base):
    __tablename__ = "sources"
    
    source_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    page_title = Column(String(500), nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    robots_allowed = Column(Boolean, nullable=True)
    http_status = Column(Integer, nullable=True)
    content_sha256 = Column(String(64), nullable=True)
    content_text = Column(Text, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="sources")

class LeadScoring(Base):
    __tablename__ = "lead_scoring"
    
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), primary_key=True)
    propensity_score = Column(Float, nullable=False)
    tier = Column(Enum("A", "B", "C", name="tier_enum"), nullable=False)
    rationale = Column(Text, nullable=False)
    reviewer_status = Column(Enum("pending", "approved", "rejected", name="reviewer_status_enum"), default="pending")
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="lead_scoring")
