import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import re

PAGESPEED_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your real key

# Weighted scoring parameters
SCORES = {
    "Meta Description": 15,
    "H1 Tag": 10,
    "Language Declared": 5,
    "Viewport Tag": 5,
    "Favicon Linked": 5,
    "Paragraphs": 10,
    "Word Count": 10,
    "Bold/Strong Tags": 5,
    "Image Alt Tags": 10,
    "Schema Markup Types": 10,
    "Google PageSpeed Score": 15
}


def ensure_scheme(url):
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url

def fetch_robots_txt(url):
    try:
        domain = urlparse(url).netloc
        robots_url = f"https://{domain}/robots.txt"
        r = requests.get(robots_url, timeout=5)
        return r.text if r.status_code == 200 else "Missing or inaccessible"
    except:
        return "Failed to fetch"

def fetch_sitemap(url):
    try:
        domain = urlparse(url).netloc
        sitemap_url = f"https://{domain}/sitemap.xml"
        r = requests.get(sitemap_url, timeout=5)
        return "Present" if r.status_code == 200 else "Missing"
    except:
        return "Failed to fetch"

def extract_schema(soup):
    scripts = soup.find_all('script', type='application/ld+json')
    schemas = []
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and '@type' in data:
                schemas.append(data['@type'])
        except:
            continue
    return schemas if schemas else ["None detected"]

def check_img_alt_tags(soup):
    imgs = soup.find_all('img')
    total = len(imgs)
    with_alt = sum(1 for img in imgs if img.get('alt'))
    without_alt = total - with_alt
    return with_alt, without_alt, total

def get_image_alt_list(soup):
    imgs = soup.find_all('img')
    report = []
    for img in imgs:
        src = img.get('src', 'N/A')
        alt = img.get('alt', 'Missing')
        report.append(f"{src} - alt: {alt if alt else 'Missing'}")
    return report[:10]

def get_headings(soup):
    headings = {}
    for tag in ['h1', 'h2', 'h3']:
        tags = soup.find_all(tag)
        headings[tag.upper()] = [t.get_text(strip=True) for t in tags]
    return headings

def fetch_pagespeed_score(url):
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    for strategy in ["mobile", "desktop"]:
        try:
            params = {
                "url": url,
                "key": PAGESPEED_API_KEY,
                "category": "performance",
                "strategy": strategy
            }
            r = requests.get(endpoint, params=params, timeout=20)
            if r.status_code == 200:
                data = r.json()
                score = data["lighthouseResult"]["categories"]["performance"]["score"]
                return int(score * 100)
        except:
            continue
    return None

def calculate_score(data):
    score = 0
    reasons = []

    if data['Meta Description'] != "Missing":
        score += SCORES['Meta Description']
    else:
        reasons.append("Missing meta description")

    if data['H1 Tag'] != "Missing":
        score += SCORES['H1 Tag']
    else:
        reasons.append("Missing H1 tag")

    if data['Language Declared'] != "Missing":
        score += SCORES['Language Declared']
    else:
        reasons.append("No language declared in HTML tag")

    if data['Viewport Tag'] == "Present":
        score += SCORES['Viewport Tag']
    else:
        reasons.append("Missing viewport meta tag")

    if data['Favicon Linked'] == "Present":
        score += SCORES['Favicon Linked']
    else:
        reasons.append("Missing favicon link")

    if data['Paragraphs'] >= 3:
        score += SCORES['Paragraphs']
    else:
        reasons.append("Too few paragraph tags")

    if data['Word Count'] >= 300:
        score += SCORES['Word Count']
    else:
        reasons.append("Low word count")

    if data['Bold/Strong Tags'] > 0:
        score += SCORES['Bold/Strong Tags']
    else:
        reasons.append("No strong or bold tags")

    with_alt, without_alt, total = data['Image Alt Tags Raw']
    if with_alt > 0:
        score += SCORES['Image Alt Tags']
    else:
        reasons.append("All images missing alt tags")

    if data['Schema Markup Types'] != "None detected":
        score += SCORES['Schema Markup Types']
    else:
        reasons.append("No schema.org structured data found")

    if isinstance(data['Google PageSpeed Score'], int):
        if data['Google PageSpeed Score'] >= 50:
            score += SCORES['Google PageSpeed Score']
        else:
            reasons.append("PageSpeed score too low")
    else:
        reasons.append("No PageSpeed score available")

    return min(score, 100), reasons

def analyze_seo(url):
    try:
        url = ensure_scheme(url)
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else "Missing"
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag['content'].strip() if description_tag else "Missing"
        h1 = soup.find("h1").text.strip() if soup.find("h1") else "Missing"

        language = soup.html.get("lang", "Missing") if soup.html else "Missing"
        viewport = "Present" if soup.find("meta", attrs={"name": "viewport"}) else "Missing"
        favicon = "Present" if soup.find("link", rel=re.compile("icon", re.I)) else "Missing"

        strong_count = len(soup.find_all("strong")) + len(soup.find_all("b"))
        paragraphs = soup.find_all("p")
        paragraph_count = len(paragraphs)
        word_count = sum(len(p.get_text(strip=True).split()) for p in paragraphs)

        headings = get_headings(soup)
        with_alt, without_alt, total = check_img_alt_tags(soup)
        alt_tag_list = get_image_alt_list(soup)
        schema_info = extract_schema(soup)
        robots_txt = fetch_robots_txt(url)
        sitemap_status = fetch_sitemap(url)
        pagespeed_score = fetch_pagespeed_score(url)

        result = {
            "Page Title": title,
            "Meta Description": description,
            "H1 Tag": h1,
            "Language Declared": language,
            "Viewport Tag": viewport,
            "Favicon Linked": favicon,
            "Paragraphs": paragraph_count,
            "Word Count": word_count,
            "Bold/Strong Tags": strong_count,
            "H1-H3 Headings": headings,
            "Image Alt Tags": f"{with_alt} with alt / {without_alt} missing alt (Total: {total})",
            "Image Alt Tags Raw": (with_alt, without_alt, total),
            "Top Image Alt Tag Examples": alt_tag_list,
            "Schema Markup Types": ", ".join(schema_info),
            "robots.txt": robots_txt[:300],
            "sitemap.xml": sitemap_status,
            "Google PageSpeed Score": pagespeed_score
        }

        score, suggestions = calculate_score(result)
        result["SEO Score"] = f"{score}%"
        result["Improvement Suggestions"] = suggestions
        return result

    except Exception as e:
        return {"error": f"Failed to analyze SEO: {e}"}

