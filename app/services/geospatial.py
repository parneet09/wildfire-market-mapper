# import rasterio
# import numpy as np
# from typing import Optional, Tuple, Dict
# from sqlalchemy import text
# from app.config import settings
# from app.db import SessionLocal, engine
# from app.models import Organization, RiskOverlay
# import logging
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# logger = logging.getLogger(__name__)

# class WildfireGeospatialService:
#     def __init__(self):
#         self.susceptibility_raster = None
#         self.ignition_raster = None
#         self.geocoder = Nominatim(user_agent="wildfire_mapper")
        
#         # Load risk rasters
#         self._load_risk_rasters()
    
#     def _load_risk_rasters(self):
#         """Load susceptibility and ignition risk rasters"""
#         try:
#             if settings.geotiff_susceptibility:
#                 self.susceptibility_raster = rasterio.open(settings.geotiff_susceptibility)
#                 logger.info("Loaded susceptibility risk raster")
            
#             if settings.geotiff_ignition:
#                 self.ignition_raster = rasterio.open(settings.geotiff_ignition)
#                 logger.info("Loaded ignition risk raster")
                
#         except Exception as e:
#             logger.warning(f"Could not load risk rasters: {e}")
    
#     def geocode_organization(self, org: Organization) -> Optional[Tuple[float, float]]:
#         """Geocode organization location using name and address"""
#         if org.latitude and org.longitude:
#             return org.latitude, org.longitude
        
#         try:
#             # Build search query
#             search_parts = [org.name]
#             if org.region_state:
#                 search_parts.append(org.region_state)
#             if org.country:
#                 search_parts.append(org.country)
            
#             search_query = ", ".join(search_parts)
            
#             # Geocode
#             location = self.geocoder.geocode(search_query, timeout=10)
            
#             if location:
#                 logger.info(f"Geocoded {org.name}: {location.latitude}, {location.longitude}")
#                 return location.latitude, location.longitude
#             else:
#                 logger.warning(f"Could not geocode {org.name}")
#                 return None
                
#         except (GeocoderTimedOut, GeocoderUnavailable) as e:
#             logger.warning(f"Geocoding timeout for {org.name}: {e}")
#             return None
#         except Exception as e:
#             logger.error(f"Geocoding error for {org.name}: {e}")
#             return None
    
#     def sample_risk_raster(self, lat: float, lon: float, raster) -> Optional[float]:
#         """Sample raster value at given coordinates"""
#         if not raster:
#             return None
        
#         try:
#             # Convert lat/lon to raster coordinates
#             row, col = raster.index(lon, lat)
            
#             # Sample the raster
#             sample = raster.read(1, window=((row, row+1), (col, col+1)))
            
#             if sample.size > 0:
#                 return float(sample[0, 0])
#             else:
#                 return None
                
#         except Exception as e:
#             logger.warning(f"Error sampling raster at {lat}, {lon}: {e}")
#             return None
    
#     def calculate_exposure_score(self, susceptibility: float, ignition: float) -> float:
#         """Calculate combined exposure score from susceptibility and ignition"""
#         if susceptibility is None or ignition is None:
#             return None
        
#         # Weighted combination
#         exposure = (settings.susceptibility_weight * susceptibility + 
#                    settings.ignition_weight * ignition)
        
#         # Normalize to 0-100 scale
#         exposure = max(0, min(100, exposure * 100))
        
#         return exposure
    
#     def update_organization_location(self, org_id: str, lat: float, lon: float):
#         """Update organization with geocoded location"""
#         db = SessionLocal()
#         try:
#             # Update organization
#             org = db.query(Organization).filter(Organization.org_id == org_id).first()
#             if org:
#                 org.latitude = lat
#                 org.longitude = lon
                
#                 # Update PostGIS geometry
#                 geom_query = text("""
#                     UPDATE organizations 
#                     SET geom = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
#                     WHERE org_id = :org_id
#                 """)
#                 db.execute(geom_query, {"lon": lon, "lat": lat, "org_id": org_id})
                
#                 db.commit()
#                 logger.info(f"Updated location for {org.name}")
            
#         except Exception as e:
#             logger.error(f"Error updating location for {org_id}: {e}")
#             db.rollback()
#         finally:
#             db.close()
    
#     def create_risk_overlay(self, org_id: str, lat: float, lon: float) -> Optional[RiskOverlay]:
#         """Create risk overlay for organization"""
#         try:
#             # Sample risk rasters
#             susceptibility = self.sample_risk_raster(lat, lon, self.susceptibility_raster)
#             ignition = self.sample_risk_raster(lat, lon, self.ignition_raster)
            
#             # Calculate exposure score
#             exposure_score = self.calculate_exposure_score(susceptibility, ignition)
            
#             # Create risk overlay
#             risk_overlay = RiskOverlay(
#                 org_id=org_id,
#                 susceptibility=susceptibility,
#                 ignition=ignition,
#                 exposure_score=exposure_score
#             )
            
#             return risk_overlay
            
#         except Exception as e:
#             logger.error(f"Error creating risk overlay for {org_id}: {e}")
#             return None
    
#     def process_organization_geospatial(self, org_id: str) -> bool:
#         """Process geospatial data for a single organization"""
#         db = SessionLocal()
#         try:
#             org = db.query(Organization).filter(Organization.org_id == org_id).first()
#             if not org:
#                 return False
            
#             # Check if already has location
#             if org.latitude and org.longitude:
#                 lat, lon = org.latitude, org.longitude
#             else:
#                 # Geocode
#                 coords = self.geocode_organization(org)
#                 if not coords:
#                     return False
                
#                 lat, lon = coords
#                 self.update_organization_location(org_id, lat, lon)
            
#             # Create risk overlay
#             risk_overlay = self.create_risk_overlay(org_id, lat, lon)
#             if risk_overlay:
#                 # Check if overlay already exists
#                 existing = db.query(RiskOverlay).filter(RiskOverlay.org_id == org_id).first()
#                 if existing:
#                     # Update existing
#                     existing.susceptibility = risk_overlay.susceptibility
#                     existing.ignition = risk_overlay.ignition
#                     existing.exposure_score = risk_overlay.exposure_score
#                 else:
#                     # Create new
#                     db.add(risk_overlay)
                
#                 db.commit()
#                 logger.info(f"Created risk overlay for {org.name}")
#                 return True
            
#             return False
            
#         except Exception as e:
#             logger.error(f"Error processing geospatial for {org_id}: {e}")
#             db.rollback()
#             return False
#         finally:
#             db.close()
    
#     def process_all_organizations(self) -> Dict[str, bool]:
#         """Process geospatial data for all organizations"""
#         db = SessionLocal()
#         try:
#             orgs = db.query(Organization).all()
#             results = {}
            
#             for org in orgs:
#                 success = self.process_organization_geospatial(org.org_id)
#                 results[org.org_id] = success
            
#             return results
            
#         except Exception as e:
#             logger.error(f"Error processing all organizations: {e}")
#             return {}
#         finally:
#             db.close()

# # Utility function for standalone geospatial processing
# def process_organization_geospatial(org_id: str) -> bool:
#     """Process geospatial data for a single organization"""
#     service = WildfireGeospatialService()
#     return service.process_organization_geospatial(org_id)

# def process_all_organizations_geospatial() -> Dict[str, bool]:
#     """Process geospatial data for all organizations"""
#     service = WildfireGeospatialService()
#     return service.process_all_organizations()











import sys, os
from typing import Optional, Tuple, Dict
import logging
import numpy as np
import rasterio
from sqlalchemy import text
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# ---------------------------------------------------------------
# ✅ Ensure project root is in sys.path before any local imports
# ---------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# ---------------------------------------------------------------
# ✅ Local imports (will now work)
# ---------------------------------------------------------------
from app.config import settings
from app.db import SessionLocal
from app.models import Organization, RiskOverlay

# ---------------------------------------------------------------
# ✅ Logger setup
# ---------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class WildfireGeospatialService:
    def __init__(self):
        self.susceptibility_raster = None
        self.ignition_raster = None
        self.geocoder = Nominatim(user_agent="wildfire_mapper")

        # Load risk rasters at initialization
        self._load_risk_rasters()

    # -----------------------------------------------------------
    # 🌍 Load GeoTIFF Rasters
    # -----------------------------------------------------------
    def _load_risk_rasters(self):
        try:
            if getattr(settings, "geotiff_susceptibility", None):
                self.susceptibility_raster = rasterio.open(settings.geotiff_susceptibility)
                logger.info("Loaded susceptibility risk raster")

            if getattr(settings, "geotiff_ignition", None):
                self.ignition_raster = rasterio.open(settings.geotiff_ignition)
                logger.info("Loaded ignition risk raster")

        except Exception as e:
            logger.warning(f"Could not load risk rasters: {e}")

    # -----------------------------------------------------------
    # 📍 Geocoding Function
    # -----------------------------------------------------------
    def geocode_organization(self, org: Organization) -> Optional[Tuple[float, float]]:
        if org.latitude and org.longitude:
            return org.latitude, org.longitude

        try:
            search_parts = [org.name]
            if org.region_state:
                search_parts.append(org.region_state)
            if org.country:
                search_parts.append(org.country)

            search_query = ", ".join(search_parts)
            location = self.geocoder.geocode(search_query, timeout=10)

            if location:
                logger.info(f"Geocoded {org.name}: {location.latitude}, {location.longitude}")
                return location.latitude, location.longitude
            else:
                logger.warning(f"Could not geocode {org.name}")
                return None

        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.warning(f"Geocoding timeout for {org.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Geocoding error for {org.name}: {e}")
            return None

    # -----------------------------------------------------------
    # 🧭 Sample Raster Values
    # -----------------------------------------------------------
    def sample_risk_raster(self, lat: float, lon: float, raster) -> Optional[float]:
        if not raster:
            return None

        try:
            row, col = raster.index(lon, lat)
            sample = raster.read(1, window=((row, row + 1), (col, col + 1)))
            if sample.size > 0:
                return float(sample[0, 0])
        except Exception as e:
            logger.warning(f"Error sampling raster at {lat}, {lon}: {e}")
        return None

    # -----------------------------------------------------------
    # 🔥 Exposure Score Calculation
    # -----------------------------------------------------------
    def calculate_exposure_score(self, susceptibility: float, ignition: float) -> Optional[float]:
        if susceptibility is None or ignition is None:
            return None

        exposure = (
            settings.susceptibility_weight * susceptibility +
            settings.ignition_weight * ignition
        )
        return max(0, min(100, exposure * 100))

    # -----------------------------------------------------------
    # 🧭 Update Organization Location
    # -----------------------------------------------------------
    def update_organization_location(self, org_id: str, lat: float, lon: float):
        db = SessionLocal()
        try:
            org = db.query(Organization).filter(Organization.org_id == org_id).first()
            if org:
                org.latitude = lat
                org.longitude = lon
                geom_query = text("""
                    UPDATE organizations 
                    SET geom = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                    WHERE org_id = :org_id
                """)
                db.execute(geom_query, {"lon": lon, "lat": lat, "org_id": org_id})
                db.commit()
                logger.info(f"Updated location for {org.name}")
        except Exception as e:
            logger.error(f"Error updating location for {org_id}: {e}")
            db.rollback()
        finally:
            db.close()

    # -----------------------------------------------------------
    # 🗺️ Create Risk Overlay
    # -----------------------------------------------------------
    def create_risk_overlay(self, org_id: str, lat: float, lon: float) -> Optional[RiskOverlay]:
        try:
            susceptibility = self.sample_risk_raster(lat, lon, self.susceptibility_raster)
            ignition = self.sample_risk_raster(lat, lon, self.ignition_raster)
            exposure_score = self.calculate_exposure_score(susceptibility, ignition)

            return RiskOverlay(
                org_id=org_id,
                susceptibility=susceptibility,
                ignition=ignition,
                exposure_score=exposure_score
            )
        except Exception as e:
            logger.error(f"Error creating risk overlay for {org_id}: {e}")
            return None

    # -----------------------------------------------------------
    # 🏢 Process One Organization
    # -----------------------------------------------------------
    def process_organization_geospatial(self, org_id: str) -> bool:
        db = SessionLocal()
        try:
            org = db.query(Organization).filter(Organization.org_id == org_id).first()
            if not org:
                return False

            if org.latitude and org.longitude:
                lat, lon = org.latitude, org.longitude
            else:
                coords = self.geocode_organization(org)
                if not coords:
                    return False
                lat, lon = coords
                self.update_organization_location(org_id, lat, lon)

            risk_overlay = self.create_risk_overlay(org_id, lat, lon)
            if risk_overlay:
                existing = db.query(RiskOverlay).filter(RiskOverlay.org_id == org_id).first()
                if existing:
                    existing.susceptibility = risk_overlay.susceptibility
                    existing.ignition = risk_overlay.ignition
                    existing.exposure_score = risk_overlay.exposure_score
                else:
                    db.add(risk_overlay)
                db.commit()
                logger.info(f"Created risk overlay for {org.name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error processing geospatial for {org_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    # -----------------------------------------------------------
    # 🌍 Process All Organizations
    # -----------------------------------------------------------
    def process_all_organizations(self) -> Dict[str, bool]:
        db = SessionLocal()
        try:
            orgs = db.query(Organization).all()
            results = {}
            for org in orgs:
                success = self.process_organization_geospatial(org.org_id)
                results[org.org_id] = success
            return results
        except Exception as e:
            logger.error(f"Error processing all organizations: {e}")
            return {}
        finally:
            db.close()


# -----------------------------------------------------------
# 🧩 Utility Functions for Script Use
# -----------------------------------------------------------
def process_organization_geospatial(org_id: str) -> bool:
    return WildfireGeospatialService().process_organization_geospatial(org_id)


def process_all_organizations_geospatial() -> Dict[str, bool]:
    return WildfireGeospatialService().process_all_organizations()
