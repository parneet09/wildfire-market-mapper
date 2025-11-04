# import asyncio
# import hashlib
# import time
# from typing import List, Dict, Optional
# from urllib.parse import urljoin, urlparse
# import httpx
# from playwright.async_api import async_playwright, Browser, Page
# from app.config import settings
# from app.db import SessionLocal
# from app.models import Source
# import logging

# logger = logging.getLogger(__name__)

# class WildfireCrawler:
#     def __init__(self):
#         self.rate_limits = {}  # domain -> last_request_time
#         self.max_depth = settings.max_crawl_depth
#         self.user_agent = settings.user_agent
#         self.timeout = settings.request_timeout
#         self.timeout = getattr(settings, "request_timeout", 60)  # default to 60s if not set

        
#     async def check_robots_txt(self, domain: str) -> bool:
#         """Check if crawling is allowed by robots.txt"""
#         try:
#             async with httpx.AsyncClient(timeout=10) as client:
#                 robots_url = f"https://{domain}/robots.txt"
#                 response = await client.get(robots_url)
#                 if response.status_code == 200:
#                     content = response.text.lower()
#                     return "disallow: /" not in content
#                 return True  # If no robots.txt, assume allowed
#         except Exception as e:
#             logger.warning(f"Error checking robots.txt for {domain}: {e}")
#             return True  # Assume allowed on error
    
#     async def rate_limit_domain(self, domain: str):
#         """Implement rate limiting per domain"""
#         if domain in self.rate_limits:
#             elapsed = time.time() - self.rate_limits[domain]
#             min_interval = 1.0 / settings.crawl_rate_per_domain
#             if elapsed < min_interval:
#                 await asyncio.sleep(min_interval - elapsed)
#         self.rate_limits[domain] = time.time()
    
#     async def extract_text_content(self, page: Page) -> str:
#         """Extract main text content from page"""
#         try:
#             # Try to get main content area
#             content_selectors = [
#                 'main',
#                 '[role="main"]',
#                 '.content',
#                 '.main-content',
#                 '#content',
#                 '#main'
#             ]
            
#             for selector in content_selectors:
#                 element = page.query_selector(selector)
#                 if element:
#                     text = await element.inner_text()
#                     if len(text.strip()) > 100:  # Ensure we have substantial content
#                         return text.strip()
            
#             # Fallback to body text
#             body = page.query_selector('body')
#             if body:
#                 return await body.inner_text()
            
#             return ""
#         except Exception as e:
#             logger.error(f"Error extracting text content: {e}")
#             return ""
    





#     async def crawl_page(self, url: str, depth: int = 0) -> Optional[Dict]:
#         """Crawl a single page and return extracted data"""
#         if depth > self.max_depth:
#             return None
            
#         domain = urlparse(url).netloc
#         await self.rate_limit_domain(domain)
        
#         try:
#             async with async_playwright() as p:
#                 browser = await p.chromium.launch(headless=True)
#                 page = await browser.new_page()
                
#                 # Set user agent
#                 await page.set_extra_http_headers({"User-Agent": self.user_agent})

#                 logger.info(f"Navigating to {url} with timeout={self.timeout}s")

                
#                 # Navigate to page
#                 await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                
#                 # Extract page information
#                 title = await page.title()
#                 content = await self.extract_text_content(page)
                
#                 # Generate content hash
#                 content_hash = hashlib.sha256(content.encode()).hexdigest()
                
#                 await browser.close()
                
#                 return {
#                     "url": url,
#                     "page_title": title,
#                     "content_text": content,
#                     "content_sha256": content_hash,
#                     "http_status": 200,
#                     "robots_allowed": True
#                 }
                
#         except Exception as e:
#             logger.error(f"Error crawling {url}: {e}")
#             return {
#                 "url": url,
#                 "page_title": None,
#                 "content_text": "",
#                 "content_sha256": None,
#                 "http_status": None,
#                 "robots_allowed": None
#             }




    
#     async def crawl_urls(self, urls: List[str]) -> List[Dict]:
#         """Crawl multiple URLs concurrently"""
#         tasks = []
#         for url in urls:
#             task = self.crawl_page(url)
#             tasks.append(task)
        
#         results = await asyncio.gather(*tasks, return_exceptions=True)
        
#         # Filter out exceptions and None results
#         valid_results = []
#         for result in results:
#             if isinstance(result, dict) and result.get("url"):
#                 valid_results.append(result)
        
#         return valid_results
    
#     def save_sources(self, sources_data: List[Dict], org_id: str):
#         """Save crawled sources to database"""
#         db = SessionLocal()
#         try:
#             for source_data in sources_data:
#                 source = Source(
#                     org_id=org_id,
#                     url=source_data["url"],
#                     page_title=source_data["page_title"],
#                     robots_allowed=source_data["robots_allowed"],
#                     http_status=source_data["http_status"],
#                     content_sha256=source_data["content_sha256"],
#                     content_text=source_data["content_text"]
#                 )
#                 db.add(source)
            
#             db.commit()
#             logger.info(f"Saved {len(sources_data)} sources for organization {org_id}")
            
#         except Exception as e:
#             logger.error(f"Error saving sources: {e}")
#             db.rollback()
#         finally:
#             db.close()

# # Utility function for standalone crawling
# async def crawl_organization_sources(org_id: str, urls: List[str]):
#     """Crawl sources for a specific organization"""
#     crawler = WildfireCrawler()
#     sources_data = await crawler.crawl_urls(urls)
#     crawler.save_sources(sources_data, org_id)
#     return sources_data


# import asyncio

# async def _fetch_async(url: str) -> str:
#     """Internal async function to fetch page text using the crawler."""
#     crawler = WildfireCrawler()
#     result = await crawler.crawl_page(url)
#     return result.get("content_text", "") if result else ""

# def fetch_text_from_url(url: str) -> str:
#     """
#     Synchronous wrapper for simple_demo.py to fetch page text.
#     Uses WildfireCrawler internally.
#     """
#     try:
#         return asyncio.run(_fetch_async(url))
#     except Exception as e:
#         return f"Error fetching {url}: {e}"







import asyncio
import hashlib
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse
import httpx
from playwright.async_api import async_playwright, Page
from app.config import settings
from app.db import SessionLocal
from app.models import Source
import logging

logger = logging.getLogger(__name__)

class WildfireCrawler:
    def __init__(self):
        self.rate_limits = {}  # domain -> last_request_time
        self.max_depth = settings.max_crawl_depth
        self.user_agent = settings.user_agent
        self.timeout = getattr(settings, "request_timeout", 60)  # default to 60s if not set

    async def check_robots_txt(self, domain: str) -> bool:
        """Check if crawling is allowed by robots.txt"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                robots_url = f"https://{domain}/robots.txt"
                response = await client.get(robots_url)
                if response.status_code == 200:
                    content = response.text.lower()
                    return "disallow: /" not in content
                return True  # If no robots.txt, assume allowed
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {domain}: {e}")
            return True  # Assume allowed on error

    async def rate_limit_domain(self, domain: str):
        """Implement rate limiting per domain"""
        if domain in self.rate_limits:
            elapsed = time.time() - self.rate_limits[domain]
            min_interval = 1.0 / settings.crawl_rate_per_domain
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
        self.rate_limits[domain] = time.time()

    async def extract_text_content(self, page: Page) -> str:
        """Extract main text content from page"""
        try:
            # Try to get main content area
            content_selectors = [
                'main',
                '[role="main"]',
                '.content',
                '.main-content',
                '#content',
                '#main'
            ]

            for selector in content_selectors:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if len(text.strip()) > 100:  # Ensure substantial content
                        return text.strip()

            # Fallback to body text
            body = await page.query_selector('body')
            if body:
                return await body.inner_text()

            return ""
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""

    async def crawl_page(self, url: str, depth: int = 0) -> Optional[Dict]:
        """Crawl a single page and return extracted data"""
        if depth > self.max_depth:
            return None

        domain = urlparse(url).netloc
        await self.rate_limit_domain(domain)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Set user agent
                await page.set_extra_http_headers({"User-Agent": self.user_agent})

                logger.info(f"Navigating to {url} with timeout={self.timeout}s")

                # Navigate to page
                await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)

                # Extract page information
                title = await page.title()
                content = await self.extract_text_content(page)

                # Generate content hash
                content_hash = hashlib.sha256(content.encode()).hexdigest()

                await browser.close()

                return {
                    "url": url,
                    "page_title": title,
                    "content_text": content,
                    "content_sha256": content_hash,
                    "http_status": 200,
                    "robots_allowed": True
                }

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return {
                "url": url,
                "page_title": None,
                "content_text": "",
                "content_sha256": None,
                "http_status": None,
                "robots_allowed": None
            }

    async def crawl_urls(self, urls: List[str]) -> List[Dict]:
        """Crawl multiple URLs concurrently"""
        tasks = [self.crawl_page(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and None results
        valid_results = [r for r in results if isinstance(r, dict) and r.get("url")]
        return valid_results

    def save_sources(self, sources_data: List[Dict], org_id: str):
        """Save crawled sources to database"""
        db = SessionLocal()
        try:
            for source_data in sources_data:
                source = Source(
                    org_id=org_id,
                    url=source_data["url"],
                    page_title=source_data["page_title"],
                    robots_allowed=source_data["robots_allowed"],
                    http_status=source_data["http_status"],
                    content_sha256=source_data["content_sha256"],
                    content_text=source_data["content_text"]
                )
                db.add(source)

            db.commit()
            logger.info(f"Saved {len(sources_data)} sources for organization {org_id}")

        except Exception as e:
            logger.error(f"Error saving sources: {e}")
            db.rollback()
        finally:
            db.close()


# Utility function for standalone crawling
async def crawl_organization_sources(org_id: str, urls: List[str]):
    """Crawl sources for a specific organization"""
    crawler = WildfireCrawler()
    sources_data = await crawler.crawl_urls(urls)
    crawler.save_sources(sources_data, org_id)
    return sources_data


async def _fetch_async(url: str) -> str:
    """Internal async function to fetch page text using the crawler."""
    crawler = WildfireCrawler()
    result = await crawler.crawl_page(url)
    return result.get("content_text", "") if result else ""


def fetch_text_from_url(url: str) -> str:
    """
    Synchronous wrapper for simple_demo.py to fetch page text.
    Uses WildfireCrawler internally.
    """
    try:
        return asyncio.run(_fetch_async(url))
    except Exception as e:
        return f"Error fetching {url}: {e}"
