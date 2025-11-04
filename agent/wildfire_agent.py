

"""
wildfire_agent.py
-----------------
AI-powered agent that analyzes wildfire-related websites using GPT-4o..
"""

import os
import re
import json
import requests
from bs4 import BeautifulSoup
import openai
from agent.report_generator import generate_wildfire_report




# ✅ Use environment variable for API key
openai.api_key = os.getenv("OPENAI_API_KEY")



import requests
from bs4 import BeautifulSoup
import re
import random

def auto_find_websites(n=5):
    """
    Searches for wildfire-related organizations and returns a list of URLs.
    """
    print(f"🌍 Searching the web for {n} wildfire-related organizations...")
    query = "wildfire management organizations site:.gov OR site:.org OR site:.ca OR site:.us"
    search_url = f"https://duckduckgo.com/html/?q={query}"

    response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('a', href=True)

    urls = []
    for link in results:
        href = link['href']
        match = re.search(r'https?://[^\s&]+', href)
        if match:
            url = match.group(0)
            if 'duckduckgo.com' not in url and 'javascript' not in url:
                urls.append(url)

    # Remove duplicates and limit to N
    unique_urls = list(dict.fromkeys(urls))[:n]
    print(f"✅ Found {len(unique_urls)} websites:")
    for u in unique_urls:
        print("   •", u)

    return unique_urls






# ---------------------------------------------------------
# 1. Fetch website content safely
# ---------------------------------------------------------
def fetch_website_text(url: str) -> str:
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Failed to fetch website: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = soup.get_text(separator=" ", strip=True)
    return text[:8000]  # stay under token limit

# ---------------------------------------------------------
# 2. Safely parse GPT JSON
# ---------------------------------------------------------
def parse_gpt_json(response_text: str) -> dict:
    """
    Extract JSON from GPT output, ignoring extra text/markdown.
    """
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}

# ---------------------------------------------------------
# 3. Analyze website using GPT-4o
# ---------------------------------------------------------
def analyze_website(url: str) -> dict:
    website_text = fetch_website_text(url)
    if not website_text:
        return {"error": "Could not fetch website content."}

    print(f"🔍 Analyzing {url} with GPT-4o...")

    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
    {"role": "system", "content": "You are an AI assistant extracting wildfire-related organization info in JSON."},
    {"role": "user", "content": f"""
Analyze the website text and return JSON with these fields:

- organization: name of the organization
- sector
- country
- role
- contacts: list of contacts (name, title, channel_type, value, verified)
- programs: list of programs (name, description, keywords)
- geospatial: latitude, longitude, susceptibility, ignition, exposure, risk_level
- lead_scoring: propensity_score, tier, base_score, bonuses (country, program, contact, exposure)

Return valid JSON only. Text: {website_text}
"""}
])



    analysis_raw = response.choices[0].message.content
    analysis_json = parse_gpt_json(analysis_raw)

    if not analysis_json:
        print(f"⚠️ Failed to parse GPT output for {url}")
        return {}

    return {"url": url, "data": analysis_json}

# ---------------------------------------------------------
# 4. Full pipeline example (multiple URLs)
# ---------------------------------------------------------
def full_pipeline(urls):
    results = []
    for url in urls:
        analysis = analyze_website(url)
        if "data" in analysis and analysis["data"]:
            results.append(analysis)
        else:
            print(f"⚠️ No organization info for {url}")
    return results


if __name__ == "__main__":
    print("🔥 WILDFIRE MARKET MAPPER ")

    import argparse
    from agent.report_generator import generate_wildfire_report

    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", type=int, help="Automatically find and analyze N wildfire websites")
    args = parser.parse_args()

    # 1️⃣ Get URLs
    if args.auto:
        urls = auto_find_websites(args.auto)
    else:
        urls_input = input("Enter website URLs (comma-separated): ")
        urls = [u.strip() for u in urls_input.split(",") if u.strip()]

    if not urls:
        print("⚠️ No URLs provided. Exiting.")
        exit(0)

    # 2️⃣ Run full pipeline
    pipeline_results = full_pipeline(urls)

    if not pipeline_results:
        print("⚠️ No results from pipeline. Exiting.")
        exit(0)

    # 3️⃣ Transform GPT results to report format
    formatted_results = []
    for r in pipeline_results:
        data = r.get("data", {})


        # Normalize contacts: always produce list of dicts
        contacts = []
        raw_contacts = data.get("contacts", {})

        if isinstance(raw_contacts, dict):
            for k, v in raw_contacts.items():
                if isinstance(v, dict):  # e.g., social_media
                    for sub_k, sub_v in v.items():
                        contacts.append({
                            "name": f"{k} - {sub_k}",
                            "title": "",
                            "channel_type": "url",
                            "value": sub_v,
                            "verified": ""
                        })
                else:
                    contacts.append({
                        "name": k,
                        "title": "",
                        "channel_type": "info",
                        "value": str(v),
                        "verified": ""
                    })
        elif isinstance(raw_contacts, list):
            for item in raw_contacts:
                if isinstance(item, str):
                    contacts.append({
                        "name": item,
                        "title": "",
                        "channel_type": "info",
                        "value": "",
                        "verified": ""
                    })
                elif isinstance(item, dict):
                    contacts.append(item)




        
        # Normalize programs: if list of strings, convert to dict with name
        programs = []
        raw_programs = data.get("programs", [])
        if isinstance(raw_programs, list):
            for p in raw_programs:
                if isinstance(p, str):
                    programs.append({"name": p, "description": ""})
                elif isinstance(p, dict):
                    programs.append(p)

        
        formatted_results = []
        for r in pipeline_results:
            data = r.get("data", {})
            formatted_results.append({
                "name": data.get("organization", ""),
                "sector": data.get("sector", ""),
                "country": data.get("country", "USA"),
                "role": data.get("role", ""),
                "website": r.get("url", ""),
                "contacts": data.get("contacts", []),
                "programs": data.get("programs", []),
                "geospatial": data.get("geospatial", {}),
                "lead_scoring": data.get("lead_scoring", {})
            })


        generate_wildfire_report(formatted_results, filename_prefix="wildfire_report")


    
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
 }


