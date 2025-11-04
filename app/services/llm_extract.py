import json
import re
from typing import List, Dict, Optional
from openai import OpenAI
from app.config import settings
from app.schemas import ExtractedOrganization, ExtractedContact, ExtractedProgram
import logging


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


logger = logging.getLogger(__name__)

class WildfireLLMExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        
    def extract_emails_and_phones(self, text: str) -> List[Dict]:
        """Extract emails and phone numbers from text using regex"""
        contacts = []
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            contacts.append({
                "channel_type": "email",
                "value": email,
                "verified_bool": True,  # Found in text
                "source_url": "extracted_from_text"
            })
        
        # Phone extraction (various formats)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\d{3}\s\d{3}\s\d{4}\b',  # 123 456 7890
            r'\b\+\d{1,3}\s\d{1,4}\s\d{1,4}\s\d{1,4}\b',  # International
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            for phone in phones:
                contacts.append({
                    "channel_type": "phone",
                    "value": phone,
                    "verified_bool": True,
                    "source_url": "extracted_from_text"
                })
        
        return contacts
    
    def create_extraction_prompt(self, url: str, text: str) -> str:
        """Create the prompt for LLM extraction"""
        return f"""
You are an expert at extracting organization information from web pages. Extract ONLY the information that is explicitly stated on the page.

URL: {url}

Page Content:
{text[:8000]}  # Limit content length

Extract the following information in JSON format:

{{
    "name": "Organization name (exact as stated)",
    "sector": "One of: Government, Utilities, Insurance/Analytics, Forestry/Timber, Agriculture, Real Estate/Property, NGO/Conservation, Technology/GIS, Academia/Research, Other",
    "role": "Brief description of their role in wildfire risk management",
    "country": "Country name (exact as stated)",
    "region_state": "State/province/region if mentioned",
    "website": "Official website URL if different from current URL",
    "programs": [
        {{
            "name": "Program name",
            "url": "Program URL if available",
            "description": "Brief description"
        }}
    ],
    "notes": "Any other relevant information about wildfire involvement"
}}

IMPORTANT RULES:
1. Only extract information explicitly stated on the page
2. Do NOT invent or infer information
3. If a field is not mentioned, use null
4. For sector, choose the closest match from the allowed values
5. Be precise with names and locations
6. Focus on wildfire-related programs and activities

Output only valid JSON:
"""
    
    async def extract_organization_data(self, url: str, text: str) -> Optional[ExtractedOrganization]:
        """Extract organization data using LLM"""
        try:
            prompt = self.create_extraction_prompt(url, text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise data extraction specialist. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to extract JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Validate required fields
            if not data.get("name") or not data.get("sector") or not data.get("country"):
                logger.warning(f"Missing required fields in extraction for {url}")
                return None
            
            # Create ExtractedOrganization object
            org = ExtractedOrganization(
                name=data["name"],
                sector=data["sector"],
                role=data.get("role"),
                country=data["country"],
                region_state=data.get("region_state"),
                website=data.get("website"),
                programs=data.get("programs", []),
                notes=data.get("notes")
            )
            
            # Add extracted contacts
            org.contacts = self.extract_emails_and_phones(text)
            
            return org
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"LLM extraction error for {url}: {e}")
            return None
    
    def validate_extraction(self, org: ExtractedOrganization) -> bool:
        """Validate extracted organization data"""
        if not org.name or len(org.name.strip()) < 2:
            return False
        
        if not org.sector or org.sector not in [
            "Government", "Utilities", "Insurance/Analytics", "Forestry/Timber",
            "Agriculture", "Real Estate/Property", "NGO/Conservation",
            "Technology/GIS", "Academia/Research", "Other"
        ]:
            return False
        
        if not org.country or len(org.country.strip()) < 2:
            return False
        
        return True
    
    async def process_source(self, source_id: str, url: str, text: str) -> Optional[ExtractedOrganization]:
        """Process a single source and extract organization data"""
        if not text or len(text.strip()) < 100:
            logger.warning(f"Insufficient text content for {url}")
            return None
        
        org = await self.extract_organization_data(url, text)
        
        if org and self.validate_extraction(org):
            logger.info(f"Successfully extracted organization: {org.name}")
            return org
        else:
            logger.warning(f"Failed to extract valid organization data from {url}")
            return None

# Utility function for standalone extraction
async def extract_from_source(source_id: str, url: str, text: str) -> Optional[ExtractedOrganization]:
    """Extract organization data from a single source"""
    extractor = WildfireLLMExtractor()
    return await extractor.process_source(source_id, url, text)



if __name__ == "__main__":
    # Simple test run
    extractor = WildfireLLMExtractor()
    test_url = "https://www.fire.ca.gov/"  # Example wildfire-related website
    test_text = "CAL FIRE is responsible for fire protection and stewardship of over 31 million acres of California’s privately-owned wildlands."

    import asyncio

    async def run_test():
        result = await extractor.extract_organization_data(test_url, test_text)
        print("🔹 LLM extraction output:", result)

    asyncio.run(run_test())



