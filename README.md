# 🔥 WildFire Market Mapper

An **AI-powered intelligent agent** that autonomously discovers, extracts, and analyzes organizations involved in **wildfire management**.  
This system integrates web automation, large language models (LLMs), and data analytics to create a **structured market map** for wildfire-related entities.

---

## 🌍 Overview

The **WildFire Market Mapper** automates the identification and analysis of organizations working in wildfire prevention, response, and research.  
It leverages **Python**, **OpenAI’s GPT models**, and **data parsing frameworks** to extract structured data from public web sources.

---

## 🎯 Core Features

- 🌐 **Web Crawling & Data Extraction** – Automatically scans wildfire-related websites  
- 🧠 **AI-based Data Structuring** – Uses GPT for semantic data understanding  
- ⚙️ **Automation Agent** – Runs the workflow autonomously  
- 📊 **Data Storage** – Saves structured information in JSON format  
- 🪶 **Error Handling & Logging** – Ensures stability and easy debugging  

---

## 🏗️ System Architecture

# 🔥 WildFire Market Mapper

An **AI-powered intelligent agent** that autonomously discovers, extracts, and analyzes organizations involved in **wildfire management**.  
This system integrates web automation, large language models (LLMs), and data analytics to create a **structured market map** for wildfire-related entities.

---

## 🌍 Overview

The **WildFire Market Mapper** automates the identification and analysis of organizations working in wildfire prevention, response, and research.  
It leverages **Python**, **OpenAI’s GPT models**, and **data parsing frameworks** to extract structured data from public web sources.

---

## 🎯 Core Features

- 🌐 **Web Crawling & Data Extraction** – Automatically scans wildfire-related websites  
- 🧠 **AI-based Data Structuring** – Uses GPT for semantic data understanding  
- ⚙️ **Automation Agent** – Runs the workflow autonomously  
- 📊 **Data Storage** – Saves structured information in JSON format  
- 🪶 **Error Handling & Logging** – Ensures stability and easy debugging  

---

## 🏗️ System Architecture

# 🔥 WildFire Market Mapper

An **AI-powered intelligent agent** that autonomously discovers, extracts, and analyzes organizations involved in **wildfire management**.  
This system integrates web automation, large language models (LLMs), and data analytics to create a **structured market map** for wildfire-related entities.

---

## 🌍 Overview

The **WildFire Market Mapper** automates the identification and analysis of organizations working in wildfire prevention, response, and research.  
It leverages **Python**, **OpenAI’s GPT models**, and **data parsing frameworks** to extract structured data from public web sources.

---

## 🎯 Core Features

- 🌐 **Web Crawling & Data Extraction** – Automatically scans wildfire-related websites  
- 🧠 **AI-based Data Structuring** – Uses GPT for semantic data understanding  
- ⚙️ **Automation Agent** – Runs the workflow autonomously  
- 📊 **Data Storage** – Saves structured information in JSON format  
- 🪶 **Error Handling & Logging** – Ensures stability and easy debugging  

---

## 🏗️ System Architecture

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Seed URLs │ ─▶ │ Web Crawler │ ─▶ │ LLM Extractor │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│
▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Export CSV │ ◀── │ Lead Scoring │ ◀── │ Geospatial │
│ Excel │ │ (A/B/C Tiers) │ │ Overlay │
└─────────────────┘ └─────────────────┘ └─────────────────┘


---

## ⚙️ Technical Components

### 1. Data Extraction Layer
- Uses **Requests** and **BeautifulSoup** to fetch and parse web content.  
- Handles dynamic pages, timeouts, and redirects for robustness.

### 2. LLM Integration
- Integrates **OpenAI GPT models** for structured data extraction.  
- Prompts are engineered to extract:
  - Organization Name  
  - Sector (Government, Private, Research, etc.)  
  - Role/Mission  
  - Country/Region  
  - Key Initiatives  
  - Contact Details  

### 3. Automation Agent
- Orchestrates the workflow:
  - Loops through URLs  
  - Extracts and cleans data  
  - Calls the LLM  
  - Stores structured results  

### 4. Data Storage
- Outputs saved in **JSON format** for compatibility and portability.

---

## 🧩 Technologies Used

| Category | Tools / Libraries |
|-----------|------------------|
| **Language** | Python 3.11+ |
| **AI / NLP** | OpenAI GPT Models |
| **Web Extraction** | Requests, BeautifulSoup |
| **Data Storage** | JSON |
| **Version Control** | Git, GitHub |
| **Environment** | macOS, VS Code |

---

# 🚀 How to Run Locally

---

## 🧩 Set Up Environment

```bash
python -m venv venv
source venv/bin/activate    # (Mac)
# OR
venv\Scripts\activate       # (Windows)

pip install -r requirements.txt


---
```markdown
## 🔑 Add Your API Key 
```bash
OPENAI_API_KEY=your_key_here

___
```markdown
## ▶️ Run the Agent
```bash
python agent/autonomous_wildfire_agent.py

___
```markdown
## 📈 Example Output
```json
{
  "organization_name": "California Department of Forestry and Fire Protection (CAL FIRE)",
  "sector": "Government",
  "role": "Wildfire suppression and forest management",
  "country": "USA",
  "contact": "https://www.fire.ca.gov/",
  "source_url": "https://www.fire.ca.gov/"
}

___
```markdown
## 🗂️ Folder Structure
```bash
wildfire-market-mapper/
├── agent/
│   └── autonomous_wildfire_agent.py
├── data/
│   └── output/
│       └── wildfire_data.json
├── utils/
│   ├── parser.py
│   └── extractor.py
├── .env
├── requirements.txt
├── README.md
└── LICENSE

__
```markdown
## 🔮 Future Improvements
Integration with PostgreSQL or MongoDB
Interactive web dashboard for visualization
Advanced ranking and filtering system
Optimized LLM prompt engineering for precision

___
```markdown
## 🏁 Conclusion
The WildFire Market Mapper showcases how AI can enhance environmental intelligence and data automation.
By combining language models, data extraction, and automation, it transforms raw web data into actionable insights for wildfire risk management and research.

___
```markdown
##👤 Author
Parneet Kaur
AI & Data Science Intern — Acara Climate
Supervised by Olivier Makuch
