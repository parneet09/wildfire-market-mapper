import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.db import SessionLocal
from app.models import Organization, Source
import logging

logger = logging.getLogger(__name__)

class WildfireDeduplicator:
    def __init__(self):
        if settings.embeddings_provider == "local":
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.model = None  # Will use OpenAI embeddings
    
    def normalize_name(self, name: str) -> str:
        """Normalize organization name for comparison"""
        if not name:
            return ""
        
        # Remove common suffixes and prefixes
        suffixes = [" inc", " corp", " llc", " ltd", " company", " co", " corporation"]
        prefixes = ["the "]
        
        normalized = name.lower().strip()
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        
        # Remove extra whitespace and punctuation
        normalized = " ".join(normalized.split())
        normalized = normalized.replace(".", "").replace(",", "")
        
        return normalized
    
    def blocking_key(self, org: Organization) -> str:
        """Create blocking key for initial grouping"""
        name = self.normalize_name(org.name)
        country = org.country.lower().strip()
        return f"{name}_{country}"
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        if self.model:
            # Use local sentence transformers
            embeddings = self.model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        else:
            # Use OpenAI embeddings (would need to implement)
            logger.warning("OpenAI embeddings not implemented for similarity")
            return 0.0
    
    def should_merge(self, org1: Organization, org2: Organization) -> bool:
        """Determine if two organizations should be merged"""
        # Check blocking key first
        if self.blocking_key(org1) != self.blocking_key(org2):
            return False
        
        # Calculate name similarity
        name_sim = self.calculate_similarity(org1.name, org2.name)
        
        # Check website similarity if available
        website_sim = 0.0
        if org1.website and org2.website:
            website_sim = self.calculate_similarity(org1.website, org2.website)
        
        # Merge if name similarity is high enough
        if name_sim > 0.92:
            return True
        
        # Merge if website similarity is very high
        if website_sim > 0.95:
            return True
        
        return False
    
    def merge_organizations(self, primary: Organization, secondary: Organization) -> Organization:
        """Merge secondary organization into primary"""
        logger.info(f"Merging {secondary.name} into {primary.name}")
        
        # Merge contacts
        for contact in secondary.contacts:
            contact.org_id = primary.org_id
        
        # Merge programs
        for program in secondary.programs:
            program.org_id = primary.org_id
        
        # Merge sources
        for source in secondary.sources:
            source.org_id = primary.org_id
        
        # Merge risk overlay if primary doesn't have one
        if not primary.risk_overlay and secondary.risk_overlay:
            secondary.risk_overlay.org_id = primary.org_id
        
        # Merge lead scoring if primary doesn't have one
        if not primary.lead_scoring and secondary.lead_scoring:
            secondary.lead_scoring.org_id = primary.org_id
        
        # Update primary organization with any missing information
        if not primary.role and secondary.role:
            primary.role = secondary.role
        
        if not primary.website and secondary.website:
            primary.website = secondary.website
        
        if not primary.region_state and secondary.region_state:
            primary.region_state = secondary.region_state
        
        if not primary.size_band and secondary.size_band:
            primary.size_band = secondary.size_band
        
        if not primary.latitude and secondary.latitude:
            primary.latitude = secondary.latitude
            primary.longitude = secondary.longitude
        
        if not primary.notes and secondary.notes:
            primary.notes = secondary.notes
        
        return primary
    
    def deduplicate_organizations(self) -> Dict[str, List[str]]:
        """Deduplicate all organizations in the database"""
        db = SessionLocal()
        try:
            # Get all organizations
            organizations = db.query(Organization).all()
            
            # Group by blocking key
            groups = {}
            for org in organizations:
                key = self.blocking_key(org)
                if key not in groups:
                    groups[key] = []
                groups[key].append(org)
            
            # Process each group for potential merges
            merged_groups = {}
            processed_orgs = set()
            
            for key, orgs in groups.items():
                if len(orgs) <= 1:
                    continue
                
                # Sort by creation date (keep oldest)
                orgs.sort(key=lambda x: x.created_at)
                
                primary = orgs[0]
                merged_orgs = [primary]
                
                for secondary in orgs[1:]:
                    if self.should_merge(primary, secondary):
                        primary = self.merge_organizations(primary, secondary)
                        merged_orgs.append(secondary)
                        processed_orgs.add(secondary.org_id)
                
                if len(merged_orgs) > 1:
                    merged_groups[primary.org_id] = [org.org_id for org in merged_orgs]
            
            # Save merged organizations
            db.commit()
            
            # Delete merged organizations
            for org_id in processed_orgs:
                db.query(Organization).filter(Organization.org_id == org_id).delete()
            
            db.commit()
            
            logger.info(f"Deduplication completed. Merged {len(merged_groups)} groups.")
            return merged_groups
            
        except Exception as e:
            logger.error(f"Error during deduplication: {e}")
            db.rollback()
            return {}
        finally:
            db.close()

# Utility function for standalone deduplication
def run_deduplication() -> Dict[str, List[str]]:
    """Run deduplication on all organizations"""
    deduplicator = WildfireDeduplicator()
    return deduplicator.deduplicate_organizations()
