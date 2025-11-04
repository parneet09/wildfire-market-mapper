from typing import Dict, List, Optional
from app.config import settings
from app.db import SessionLocal
from app.models import Organization, LeadScoring, RiskOverlay
import logging

from app.config import settings
from app.db import SessionLocal


logger = logging.getLogger(__name__)

class WildfireLeadScorer:
    def __init__(self):
        self.sector_base_scores = settings.sector_base_scores
        self.priority_countries = settings.priority_countries
        self.wildfire_program_bonus = settings.wildfire_program_bonus
        self.verified_email_bonus = settings.verified_email_bonus
        self.priority_country_bonus = settings.priority_country_bonus
        self.tier_a_threshold = settings.tier_a_threshold
        self.tier_b_threshold = settings.tier_b_threshold
    
    def calculate_base_score(self, org: Organization) -> float:
        """Calculate base score from sector"""
        sector = org.sector
        if sector in self.sector_base_scores:
            return float(self.sector_base_scores[sector])
        return 10.0  # Default score for unknown sectors
    
    def calculate_exposure_bonus(self, org: Organization) -> float:
        """Calculate bonus from exposure score"""
        if not org.risk_overlay or not org.risk_overlay.exposure_score:
            return 0.0
        
        # Exposure score is already 0-100, so use it directly
        return org.risk_overlay.exposure_score * 0.4
    
    def calculate_program_bonus(self, org: Organization) -> float:
        """Calculate bonus from wildfire-related programs"""
        if not org.programs:
            return 0.0
        
        wildfire_keywords = [
            "wildfire", "fire", "WUI", "mitigation", "PSPS", 
            "underwriting", "hazard", "risk assessment", "emergency"
        ]
        
        bonus = 0.0
        for program in org.programs:
            program_text = f"{program.name} {program.description or ''}".lower()
            for keyword in wildfire_keywords:
                if keyword in program_text:
                    bonus += self.wildfire_program_bonus
                    break  # Only count once per program
        
        return min(bonus, self.wildfire_program_bonus * 3)  # Cap at 3x bonus
    
    def calculate_contact_bonus(self, org: Organization) -> float:
        """Calculate bonus from verified contacts"""
        if not org.contacts:
            return 0.0
        
        verified_contacts = [c for c in org.contacts if c.verified_bool]
        if verified_contacts:
            return float(self.verified_email_bonus)
        
        return 0.0
    
    def calculate_country_bonus(self, org: Organization) -> float:
        """Calculate bonus from priority country"""
        if org.country in self.priority_countries:
            return float(self.priority_country_bonus)
        return 0.0
    
    def calculate_propensity_score(self, org: Organization) -> float:
        """Calculate total propensity score for organization"""
        try:
            # Base score from sector
            base_score = self.calculate_base_score(org)
            
            # Exposure bonus
            exposure_bonus = self.calculate_exposure_bonus(org)
            
            # Program bonus
            program_bonus = self.calculate_program_bonus(org)
            
            # Contact bonus
            contact_bonus = self.calculate_contact_bonus(org)
            
            # Country bonus
            country_bonus = self.calculate_country_bonus(org)
            
            # Calculate total score
            total_score = base_score + exposure_bonus + program_bonus + contact_bonus + country_bonus
            
            # Ensure score is within 0-100 range
            total_score = max(0.0, min(100.0, total_score))
            
            logger.info(f"Calculated score for {org.name}: base={base_score}, exposure={exposure_bonus}, "
                       f"program={program_bonus}, contact={contact_bonus}, country={country_bonus}, total={total_score}")
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating propensity score for {org.name}: {e}")
            return 0.0
    
    def determine_tier(self, propensity_score: float) -> str:
        """Determine tier based on propensity score"""
        if propensity_score >= self.tier_a_threshold:
            return "A"
        elif propensity_score >= self.tier_b_threshold:
            return "B"
        else:
            return "C"
    
    def generate_rationale(self, org: Organization, propensity_score: float) -> str:
        """Generate human-readable rationale for the score"""
        rationale_parts = []
        
        # Sector explanation
        sector_score = self.calculate_base_score(org)
        rationale_parts.append(f"Base sector score: {sector_score} ({org.sector})")
        
        # Exposure explanation
        if org.risk_overlay and org.risk_overlay.exposure_score:
            exposure_bonus = self.calculate_exposure_bonus(org)
            rationale_parts.append(f"Exposure bonus: {exposure_bonus:.1f}")
        
        # Program explanation
        program_bonus = self.calculate_program_bonus(org)
        if program_bonus > 0:
            rationale_parts.append(f"Wildfire program bonus: {program_bonus}")
        
        # Contact explanation
        contact_bonus = self.calculate_contact_bonus(org)
        if contact_bonus > 0:
            rationale_parts.append(f"Verified contact bonus: {contact_bonus}")
        
        # Country explanation
        country_bonus = self.calculate_country_bonus(org)
        if country_bonus > 0:
            rationale_parts.append(f"Priority country bonus: {country_bonus}")
        
        return "; ".join(rationale_parts)
    
    def score_organization(self, org_id: str) -> Optional[LeadScoring]:
        """Score a single organization"""
        db = SessionLocal()
        try:
            org = db.query(Organization).filter(Organization.org_id == org_id).first()
            if not org:
                return None
            
            # Calculate propensity score
            propensity_score = self.calculate_propensity_score(org)
            
            # Determine tier
            tier = self.determine_tier(propensity_score)
            
            # Generate rationale
            rationale = self.generate_rationale(org, propensity_score)
            
            # Create or update lead scoring
            existing = db.query(LeadScoring).filter(LeadScoring.org_id == org_id).first()
            
            if existing:
                # Update existing
                existing.propensity_score = propensity_score
                existing.tier = tier
                existing.rationale = rationale
                lead_scoring = existing
            else:
                # Create new
                lead_scoring = LeadScoring(
                    org_id=org_id,
                    propensity_score=propensity_score,
                    tier=tier,
                    rationale=rationale,
                    reviewer_status="pending"
                )
                db.add(lead_scoring)
            
            db.commit()
            logger.info(f"Scored {org.name}: {propensity_score} ({tier})")
            
            return lead_scoring
            
        except Exception as e:
            logger.error(f"Error scoring organization {org_id}: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def score_all_organizations(self) -> Dict[str, bool]:
        """Score all organizations in the database"""
        db = SessionLocal()
        try:
            orgs = db.query(Organization).all()
            results = {}
            
            for org in orgs:
                success = self.score_organization(org.org_id) is not None
                results[org.org_id] = success
            
            return results
            
        except Exception as e:
            logger.error(f"Error scoring all organizations: {e}")
            return {}
        finally:
            db.close()

# Utility function for standalone scoring
def score_organization(org_id: str) -> Optional[LeadScoring]:
    """Score a single organization"""
    scorer = WildfireLeadScorer()
    return scorer.score_organization(org_id)

def score_all_organizations() -> Dict[str, bool]:
    """Score all organizations"""
    scorer = WildfireLeadScorer()
    return scorer.score_all_organizations()



