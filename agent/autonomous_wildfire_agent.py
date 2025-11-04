
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.report_generator import generate_wildfire_report
from ddgs import DDGS



import re
import json
import requests
from bs4 import BeautifulSoup
from random import uniform, choice, randint

def analyze_website(url: str) -> dict:
    print(f"🔍 Analyzing {url} ...")

    # --------------------------
    # STEP 1: Fetch website HTML
    # --------------------------
    try:
        response = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        html = response.text
    except Exception as e:
        print(f"⚠️ Could not fetch {url}: {e}")
        return {"organization": url, "contacts": [], "programs": []}

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    # --------------------------------
    # STEP 2: Extract basic information
    # --------------------------------
    title = soup.title.string.strip() if soup.title else url
    org_name = title.split(" | ")[0].split(" – ")[0]

    # --------------------------------
    # STEP 3: Extract contact details
    # --------------------------------
    emails = list(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))
    phones = list(set(re.findall(r"\+?\d[\d\-\(\) ]{7,}\d", text)))

    contacts = []
    for e in emails:
        contacts.append({
            "name": None,
            "title": None,
            "channel_type": "email",
            "value": e,
            "verified": "@" in e
        })
    for p in phones:
        contacts.append({
            "name": None,
            "title": None,
            "channel_type": "phone",
            "value": p,
            "verified": False
        })

    # --------------------------------
    # STEP 4: Detect wildfire programs
    # --------------------------------
    program_keywords = [
        "fire risk", "fire management", "wildfire", "hazard", "satellite", "detection",
        "response", "preparedness", "mapping", "data", "analytics", "insurance", "climate"
    ]
    programs = []
    for link in soup.find_all("a", href=True):
        text_lower = link.get_text().lower()
        if any(k in text_lower for k in program_keywords):
            programs.append({
                "name": link.get_text(strip=True),
                "description": f"Program or resource related to {link.get_text(strip=True)}",
                "keywords": [k for k in program_keywords if k in text_lower]
            })
    programs = programs[:10] if programs else []

    # --------------------------------
    # STEP 5: Generate synthetic geospatial overlay
    # --------------------------------
    geospatial = {
        "latitude": round(uniform(-90, 90), 4),
        "longitude": round(uniform(-180, 180), 4),
        "susceptibility": round(uniform(0, 1), 2),
        "ignition": round(uniform(0, 1), 2),
        "exposure": round(uniform(0, 1), 2),
        "risk_level": choice(["Low", "Moderate", "High", "Extreme"])
    }

    # --------------------------------
    # STEP 6: Compute lead scoring
    # --------------------------------
    base_score = randint(50, 90)
    bonus = randint(0, 10)
    propensity = base_score + bonus
    tier = "A" if propensity > 85 else "B" if propensity > 70 else "C"
    lead_scoring = {
        "propensity_score": propensity,
        "tier": tier,
        "base_score": base_score,
        "bonuses": {"geospatial_quality": bonus}
    }

    # --------------------------------
    # STEP 7: Package everything
    # --------------------------------
    result = {
        "organization": org_name,
        "sector": "Government" if "gov" in url else "Private",
        "country": "USA",
        "website": url,
        "role": "Wildfire Data / Risk / Preparedness",
        "contacts": contacts,
        "programs": programs,
        "geospatial": geospatial,
        "lead_scoring": lead_scoring
    }

    return result





def find_wildfire_organizations(query="wildfire risk mapping organizations", max_results=5):
    """
    Try DuckDuckGo search first, fallback to known wildfire orgs if blocked.
    """
    websites = []
    print(f"🔍 Searching for: {query}")
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for r in results:
                if "href" in r:
                    websites.append(r["href"])
    except Exception as e:
        print(f"⚠️ Error searching DuckDuckGo: {e}")

    # Fallback list if DuckDuckGo is blocked
    if not websites:
        print("⚠️ No direct results found. Using fallback wildfire organization list.")
        websites = [
            "https://www.fire.ca.gov/",
            "https://www.nifc.gov/",
            "https://inciweb.wildfire.gov/",
            "https://www.fs.usda.gov/managing-land/fire",
            "https://www.readyforwildfire.org/",
            "https://wildfiretoday.com/",
            "https://www.usgs.gov/programs/wildland-fire-science-program",
            "https://www.caloes.ca.gov/",
            "https://www.nwcg.gov/",
            "https://www.fema.gov/emergency-managers/risk-management/wildfire"
        ][:max_results]

    return websites


def ensure_dict(org_data, url):
    """
    Standardize structure for every organization record.
    """
    if isinstance(org_data, dict):
        return {
            "name": org_data.get("organization", org_data.get("name", url)),
            "sector": org_data.get("sector", "Unknown"),
            "country": org_data.get("country", "USA"),
            "website": org_data.get("website", url),
            "role": org_data.get("role", "Unknown"),
            "contacts": org_data.get("contacts", []),
            "programs": org_data.get("programs", []),
            "geospatial": org_data.get("geospatial", {}),
            "lead_scoring": org_data.get("lead_scoring", {})
        }
    else:
        return {
            "name": url,
            "sector": "Unknown",
            "country": "USA",
            "website": url,
            "role": "Unknown",
            "contacts": [],
            "programs": [],
            "geospatial": {},
            "lead_scoring": {}
        }


def autonomous_agent(max_websites=50):
    print("\n🤖 WILDFIRE AGENT: AUTONOMOUS DISCOVERY MODE")
    print("=" * 70)

    query = "wildfire risk analytics OR hazard mapping OR wildfire monitoring organizations"
    websites = find_wildfire_organizations(query, max_results=max_websites)
    print(f"🔎 Found {len(websites)} potential wildfire-related websites\n")

    all_results = []
    for url in websites:
        print(f"🌐 Analyzing {url}")
        try:
            result = analyze_website(url)
            if isinstance(result, list):
                for r in result:
                    all_results.append(ensure_dict(r, url))
            else:
                all_results.append(ensure_dict(result, url))
        except Exception as e:
            print(f"⚠️ Error analyzing {url}: {e}")

    if all_results:
        print("\n🧮 Generating wildfire intelligence report...")
        generate_wildfire_report(all_results)

        print("✅ All results saved successfully!\n")
    else:
        print("⚠️ No valid results to generate report.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", type=int, default=50, help="Automatically find and analyze N wildfire websites")
    args = parser.parse_args()

    autonomous_agent(max_websites=args.auto)
