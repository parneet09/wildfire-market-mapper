#!/usr/bin/env python3
"""
Seed data worker - loads initial URLs from CSV into the database
"""
import csv
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.db import SessionLocal
from app.models import Source
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_seed_urls():
    """Load seed URLs from CSV file"""
    db = SessionLocal()
    try:
        # Read seed URLs from CSV
        csv_path = Path("data/seeds/seed_urls.csv")
        if not csv_path.exists():
            logger.error(f"Seed CSV not found at {csv_path}")
            return
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            urls = [row['url'] for row in reader]
        
        logger.info(f"Found {len(urls)} seed URLs")
        
        # Create placeholder sources for each URL
        for url in urls:
            # Check if source already exists
            existing = db.query(Source).filter(Source.url == url).first()
            if existing:
                logger.info(f"Source already exists: {url}")
                continue
            
            # Create placeholder source (will be filled by crawler)
            source = Source(
                source_id=uuid.uuid4(),
                org_id=uuid.uuid4(),  # Temporary placeholder
                url=url,
                page_title=None,
                robots_allowed=None,
                http_status=None,
                content_sha256=None,
                content_text=None
            )
            db.add(source)
        
        db.commit()
        logger.info(f"Successfully loaded {len(urls)} seed URLs")
        
    except Exception as e:
        logger.error(f"Error loading seed URLs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_seed_urls()
