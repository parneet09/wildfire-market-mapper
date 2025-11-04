import csv
from datetime import datetime

def generate_wildfire_report(results, filename_prefix="wildfire_data"):
    """
    Takes a list of organization data dictionaries and outputs both:
    1. A formatted text report (STEP 1–7 structure)
    2. A CSV export for Excel
    Also prints the report to the console.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_filename = f"{filename_prefix}_report_{timestamp}.txt"
    csv_filename = f"{filename_prefix}_export_{timestamp}.csv"

    report_lines = []
    report_lines.append("STEP 1: AI-Powered Data Extraction")
    report_lines.append("----------------------------------------")

    for org in results:
        report_lines.append("Organization:")
        report_lines.append(f"   • Name: {org.get('name', '')}")
        report_lines.append(f"   • Sector: {org.get('sector', '')}")
        report_lines.append(f"   • Country: {org.get('country', '')}")
        report_lines.append(f"   • Website: {org.get('website', '')}")
        report_lines.append(f"   • Role: {org.get('role', '')}\n")

        report_lines.append("Contacts:")
        for c in org.get("contacts", []):
            report_lines.append(f"   • {c.get('name', '')}, {c.get('title', '')}, "
                                f"{c.get('channel_type', '')}, {c.get('value', '')}, "
                                f"Verified: {c.get('verified', '')}")
        report_lines.append("\nPrograms:")
        for p in org.get("programs", []):
            report_lines.append(f"   • {p.get('name', '')} – {p.get('description', '')} "
                                f"({p.get('keywords', '')})")

        report_lines.append("\nSTEP 2: Geospatial Risk Overlay")
        report_lines.append("----------------------------------------")
        geo = org.get("geospatial", {})
        report_lines.append(f"Latitude: {geo.get('latitude', '')}")
        report_lines.append(f"Longitude: {geo.get('longitude', '')}")
        report_lines.append(f"Susceptibility Score: {geo.get('susceptibility', '')}")
        report_lines.append(f"Ignition Score: {geo.get('ignition', '')}")
        report_lines.append(f"Exposure Score: {geo.get('exposure', '')}")
        report_lines.append(f"Risk Level: {geo.get('risk_level', '')}")

        report_lines.append("\nSTEP 3: Lead Scoring & Tier Classification")
        report_lines.append("----------------------------------------")
        lead = org.get("lead_scoring", {})
        report_lines.append(f"Propensity Score: {lead.get('propensity_score', '')}")
        report_lines.append(f"Tier: {lead.get('tier', '')}")
        report_lines.append(f"Base Score: {lead.get('base_score', '')}")
        report_lines.append("Bonuses:")
        for k, v in lead.get("bonuses", {}).items():
            report_lines.append(f"   • {k}: {v}")

        report_lines.append("\n" + "-" * 80 + "\n")

    
    # STEP 4: Summary Statistics
    report_lines.append("\n📈 STEP 4: Summary Statistics")
    report_lines.append("----------------------------------------")

    if results:
        tier_counts = {}
        sector_counts = {}
        total_exposure = 0
        total_propensity = 0

    for r in results:
        tier = r.get("lead_scoring", {}).get("tier", "Unknown")
        sector = r.get("sector", "Unknown")
        exposure = r.get("geospatial", {}).get("exposure") or 0
        propensity = r.get("lead_scoring", {}).get("propensity_score") or 0

        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        try:
            total_exposure += float(exposure)
        except (TypeError, ValueError):
            continue

        total_propensity += propensity

    avg_exposure = total_exposure / len(results)
    avg_propensity = total_propensity / len(results)

    report_lines.append(f"By Tier: {tier_counts}")
    report_lines.append(f"By Sector: {sector_counts}")
    report_lines.append(f"Average Exposure Score: {avg_exposure:.1f}")
    report_lines.append(f"Average Propensity Score: {avg_propensity:.1f}")

    # STEP 5: Recommendations
    report_lines.append("\n🎯 STEP 5: Recommendations & Next Actions")
    report_lines.append("----------------------------------------")

    tier_a_orgs = [r for r in results if r.get("lead_scoring", {}).get("tier") == "A"]
    tier_b_orgs = [r for r in results if r.get("lead_scoring", {}).get("tier") == "B"]

    report_lines.append(f"🎯 Priority Targets (Tier A): {len(tier_a_orgs)} organizations")
    for org in tier_a_orgs:
        report_lines.append(f"   • {org.get('name', '')} – Score: {org.get('lead_scoring', {}).get('propensity_score', '')}")

    report_lines.append(f"\n📋 Secondary Targets (Tier B): {len(tier_b_orgs)} organizations")
    for org in tier_b_orgs:
        report_lines.append(f"   • {org.get('name', '')} – Score: {org.get('lead_scoring', {}).get('propensity_score', '')}")

    report_lines.append("\n✅ Recommended Actions:")
    report_lines.append("   • Prioritize engagement with Tier A organizations for immediate outreach.")
    report_lines.append("   • Conduct risk mitigation discussions for regions with high exposure.")
    report_lines.append("   • Reassess Tier C leads every quarter based on new geospatial data.")
    report_lines.append("   • Update partner database after each wildfire season.\n")

    # --- PRINT TO CONSOLE ---
    print("\n".join(report_lines))

    # --- SAVE TO TXT FILE ---
    with open(txt_filename, "w", encoding="utf-8") as txt_file:
        txt_file.write("\n".join(report_lines))

    # --- CSV EXPORT (SUMMARY TABLE) ---
    csv_headers = [
        "org_name", "sector", "country", "region_state", "website",
        "exposure_score", "propensity_score", "tier", "risk_level"
    ]
    with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        writer.writeheader()
        for org in results:
            geo = org.get("geospatial", {})
            lead = org.get("lead_scoring", {})
            writer.writerow({
                "org_name": org.get("name", ""),
                "sector": org.get("sector", ""),
                "country": org.get("country", ""),
                "region_state": org.get("region_state", ""),
                "website": org.get("website", ""),
                "exposure_score": geo.get("exposure", ""),
                "propensity_score": lead.get("propensity_score", ""),
                "tier": lead.get("tier", ""),
                "risk_level": geo.get("risk_level", "")
            })

    print(f"✅ Report saved to: {txt_filename}")
    print(f"✅ CSV export saved to: {csv_filename}")
