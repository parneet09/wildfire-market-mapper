# from pydantic_settings import BaseSettings
# from typing import Dict, List, Literal
# import json


# #from app.config import settings
# #from app.db import SessionLocal



# class Settings(BaseSettings):
#     # Application
#     app_env: str = "dev"
#     debug: bool = True
    
#     # Database
#     database_url: str = "sqlite:///./test.db"  # Use SQLite for testing
    
#     # AI/LLM
#     openai_api_key: str = ""
#     embeddings_provider: str = "openai"
#     embeddings_model: str = "text-embedding-3-large"
#     llm_model: str = "gpt-4o"
    
#     # Web Scraping
#     crawl_rate_per_domain: float = 0.2
#     user_agent: str = "WildfireMapperBot/1.0 (+contact@example.com)"
#     max_crawl_depth: int = 2
#     request_timeout: int = 30
    
#     # Geospatial
#     geotiff_susceptibility: str = "data/risk_layers/susceptibility.tif"
#     geotiff_ignition: str = "data/risk_layers/ignition.tif"
    
#     # Risk Scoring
#     susceptibility_weight: float = 0.6
#     ignition_weight: float = 0.4
    
#     # Sector base scores
#     sector_base_scores: Dict[str, int] = {
#         "Utilities": 25,
#         "Insurance/Analytics": 25,
#         "Government": 20,
#         "Forestry/Timber": 15,
#         "Agriculture": 10,
#         "Technology/GIS": 10,
#         "NGO/Conservation": 10,
#         "Real Estate/Property": 10
#     }
    
#     # Priority countries
#     priority_countries: List[str] = ["USA", "Canada", "Australia"]
    
#     # Signal bonuses
#     wildfire_program_bonus: int = 10
#     verified_email_bonus: int = 8
#     priority_country_bonus: int = 6
    
#     # Tier thresholds
#     tier_a_threshold: int = 70
#     tier_b_threshold: int = 40
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False

# settings = Settings()


# # app/config.py

# class Settings:
#     def __init__(self):
#         self.sector_base_scores = {
#             "Government": 70,
#             "Insurance": 80,
#             "Research": 60,
#             "Utilities": 75,
#             "Environmental": 65
#         }

#         self.priority_countries = ["USA", "Canada", "Australia"]
#         self.wildfire_program_bonus = 5
#         self.verified_email_bonus = 3
#         self.priority_country_bonus = 4
#         self.tier_a_threshold = 70
#         self.tier_b_threshold = 50


# settings = Settings()









# app/config.py

# class Settings:
#     def __init__(self):
#         # Debug mode
#         self.debug = False  # Set to True if you want SQLAlchemy logs printed

#         # Database
#         self.database_url = "sqlite:///./wildfire.db"  # or your PostgreSQL URL

#         # GeoTIFF paths
#         self.geotiff_susceptibility = "data/susceptibility.tif"
#         self.geotiff_ignition = "data/ignition.tif"

#         # Scoring weights
#         self.susceptibility_weight = 0.6
#         self.ignition_weight = 0.4

#         # Lead scoring settings
#         self.sector_base_scores = {
#             "Government": 70,
#             "Insurance": 80,
#             "Research": 60,
#             "Utilities": 75,
#             "Environmental": 65,
#         }

#         self.priority_countries = ["USA", "Canada", "Australia"]
#         self.wildfire_program_bonus = 5
#         self.verified_email_bonus = 3
#         self.priority_country_bonus = 4
#         self.tier_a_threshold = 70
#         self.tier_b_threshold = 50


# settings = Settings()



import os


# app/config.py

class Settings:
    def __init__(self):
        # Debug mode
        self.debug = False  # Set to True if you want SQLAlchemy logs printed

        # Database
        self.database_url = "sqlite:///./wildfire.db"  # or your PostgreSQL URL

        # 🔹 OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_model = "gpt-4o-mini"

        # GeoTIFF paths
        self.geotiff_susceptibility = "data/susceptibility.tif"
        self.geotiff_ignition = "data/ignition.tif"

        # Scoring weights
        self.susceptibility_weight = 0.6
        self.ignition_weight = 0.4

        # Lead scoring settings
        self.sector_base_scores = {
            "Government": 70,
            "Insurance": 80,
            "Research": 60,
            "Utilities": 75,
            "Environmental": 65,
        }

        self.priority_countries = ["USA", "Canada", "Australia"]
        self.wildfire_program_bonus = 5
        self.verified_email_bonus = 3
        self.priority_country_bonus = 4
        self.tier_a_threshold = 70
        self.tier_b_threshold = 50


settings = Settings()
