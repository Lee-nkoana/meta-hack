import os
import sys
import time
import json
import asyncio
from playwright.async_api import async_playwright
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add backend directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.medication import Medication
from app.database import Base
from app.config import settings

# Setup Database
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

BASE_URL = "https://www.drugs.com"

async def scrape_medication_details(page, url):
    """Scrapes uses and side effects from a medication page using Playwright."""
    try:
        print(f"Navigating to {url}")
        await page.goto(url, timeout=90000, wait_until="domcontentloaded")
        
        # Generic extraction helper
        async def extract_section(header_text):
            # Find h2 with text
            try:
                # Basic logic: find h2, get following text until next h2
                # This is tricky with pure selectors. We can use evaluate to traverse DOM.
                text = await page.evaluate(f"""(headerText) => {{
                    const headers = Array.from(document.querySelectorAll('h2'));
                    const target = headers.find(h => h.textContent.includes(headerText));
                    if (!target) return "";
                    
                    let content = "";
                    let curr = target.nextElementSibling;
                    while (curr && curr.tagName !== 'H2') {{
                        content += curr.innerText + "\\n";
                        curr = curr.nextElementSibling;
                    }}
                    return content;
                }}""", header_text)
                return text.strip()
            except Exception as e:
                print(f"Error extracting {header_text}: {e}")
                return ""

        uses_text = await extract_section("Uses")
        side_effects_text = await extract_section("Side Effects")
        
        return uses_text, side_effects_text

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None

async def main():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        # Strategy: Visit a.html, get sub-links (Ab, Ac...), visit them until we have 200 meds.
        base_alpha_url = "https://www.drugs.com/alpha/a.html"
        print(f"Fetching sub-indexes from {base_alpha_url}...")
        try:
            await page.goto(base_alpha_url, timeout=90000, wait_until="domcontentloaded")
        except Exception as e:
            print(f"Failed to load alpha list: {e}")
            await browser.close()
            return

        # Extract sub-index links (Ab, Ac, Ad...)
        sub_links = await page.evaluate(f"""() => {{
            const base = "{BASE_URL}";
            const contentBox = document.querySelector('div#content') || document.querySelector('div.contentBox') || document.querySelector('div.ddc-media-list');
            if (!contentBox) return [];
            
            // Get all links
            const anchors = Array.from(contentBox.querySelectorAll('ul li a'));
            return anchors.map(a => ({{
                name: a.innerText,
                url: a.href.startsWith('http') ? a.href : base + a.getAttribute('href')
            }})).filter(l => l.name.length <= 2 || l.name.includes('-')); 
        }}""")
        
        print(f"Found {len(sub_links)} sub-indexes (Ab, Ac...). Processing...")
        
        scraped_meds = []
        total_count = 0
        target_count = 200
        
        for sub in sub_links:
            if total_count >= target_count: break
            
            print(f"Visiting Sub-Index: {sub['name']} ({sub['url']})")
            try:
                await page.goto(sub['url'], timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"Failed to load {sub['url']}: {e}")
                continue
                
            # Now extract drugs from this sub-page
            drug_links = await page.evaluate(f"""() => {{
                const base = "{BASE_URL}";
                const contentBox = document.querySelector('div#content') || document.querySelector('div.contentBox') || document.querySelector('div.ddc-media-list');
                if (!contentBox) return [];
                
                const anchors = Array.from(contentBox.querySelectorAll('ul li a'));
                return anchors.map(a => ({{
                    name: a.innerText,
                    url: a.href.startsWith('http') ? a.href : base + a.getAttribute('href')
                }}));
            }}""")
            
            # Process drugs on this page
            for item in drug_links:
                if total_count >= target_count: break
                
                name = item['name']
                url = item['url']
                
                # Exclude navigation links (single letter etc)
                if len(name) <= 2 or " - " in name: continue
                
                # Check duplication in current run
                if name in scraped_meds: continue
                
                print(f"Processing {name}...")
                
                # Check db
                exists = db.query(Medication).filter(Medication.name == name).first()
                if exists:
                    print(f"Skipping {name}, already exists.")
                    scraped_meds.append(name)
                    total_count += 1
                    continue
                
                uses, side_effects = await scrape_medication_details(page, url)
                
                if uses or side_effects:
                    med = Medication(
                        name=name,
                        url=url,
                        uses=uses,
                        side_effects=side_effects
                    )
                    db.add(med)
                    db.commit()
                    
                    # Store for JSONL export
                    entry = {}
                    # Write immediately to file to be safe/simple
                    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, "medications_training.jsonl")
                    mode = "a" # Always append
                    with open(output_path, mode) as f:
                        if uses:
                            f.write(json.dumps({"prompt": f"What are the uses of {name}?", "completion": uses}) + "\n")
                        if side_effects:
                            f.write(json.dumps({"prompt": f"What are the side effects of {name}?", "completion": side_effects}) + "\n")
                    
                    scraped_meds.append(name)
                    total_count += 1
                
                await asyncio.sleep(0.5) # Polite delay
                
        await browser.close()

    # Generate README
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    readme_path = os.path.join(output_dir, "MEDICATIONS_README.md")
    with open(readme_path, "w") as f:
        f.write("# Scraped Medications\n\n")
        f.write(f"Total Count: {len(scraped_meds)}\n\n")
        f.write("This file lists the medications available in the training dataset. Use these names to test the model's ability to identify uses and adverse reactions.\n\n")
        f.write("| Medication Name |\n")
        f.write("| --- |\n")
        for med in scraped_meds:
            f.write(f"| {med} |\n")
    print(f"Generated README at {readme_path}")

if __name__ == "__main__":
    asyncio.run(main())
