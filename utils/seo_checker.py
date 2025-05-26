import requests
from bs4 import BeautifulSoup
import re
import time

def analyze_seo(url):
    result = {}

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=10)
        load_time = round(time.time() - start_time, 2)
    except Exception as e:
        result["error"] = str(e)
        return result

    soup = BeautifulSoup(response.text, "html.parser")

    # Title and Meta
    title = soup.title.string.strip() if soup.title and soup.title.string else "Missing"
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and "content" in meta_desc_tag.attrs else "Missing"

    result["Page Title"] = title
    result["Meta Description"] = meta_desc

    # Viewport
    viewport = soup.find("meta", attrs={"name": "viewport"})
    result["Viewport Tag"] = "Present" if viewport else "Missing"

    # Favicon
    favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    result["Favicon Linked"] = "Present" if favicon else "Missing"

    # robots.txt
    try:
        robots_resp = requests.get(f"{url.rstrip('/')}/robots.txt", timeout=5)
        result["robots.txt"] = "Present" if robots_resp.status_code == 200 else "Missing"
    except:
        result["robots.txt"] = "Failed to fetch"

    # Language
    html_tag = soup.find("html")
    result["Language Declared"] = html_tag.get("lang", "Missing") if html_tag else "Missing"

    # Page Quality
    text = soup.get_text(separator=" ").strip()
    word_count = len(text.split())
    placeholder_detected = "lorem ipsum" in text.lower()
    bullet_points = bool(soup.find(["ul", "ol"]))
    paragraphs = soup.find_all("p")
    h1_in_body = bool(soup.body.find("h1")) if soup.body else False

    result["Word Count"] = word_count
    result["Has Placeholder Text"] = placeholder_detected
    result["Has Bullet Points"] = bullet_points
    result["Paragraph Count"] = len(paragraphs)
    result["H1 in Body Text"] = h1_in_body

    # Page Structure
    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")
    h3_tags = soup.find_all("h3")

    result["H1 Count"] = len(h1_tags)
    result["H2 Count"] = len(h2_tags)
    result["H3 Count"] = len(h3_tags)
    result["Heading Hierarchy Valid"] = len(h1_tags) <= 1

    empty_links = soup.find_all("a", string=lambda text: text is None or text.strip() == "")
    result["Has Empty Links"] = len(empty_links) > 0

    semantic_tags = soup.find_all(["section", "article", "nav", "aside", "main", "header", "footer"])
    result["Has Semantic Tags"] = len(semantic_tags) > 0

    # Performance Metrics
    html_size_kb = round(len(response.text.encode("utf-8")) / 1024, 2)
    total_assets = len(soup.find_all(["img", "script", "link"]))
    headers_combined = " ".join([f"{k}: {v}" for k, v in response.headers.items()])

    result["Page Load Time"] = load_time
    result["HTML Size (KB)"] = html_size_kb
    result["Total Assets"] = total_assets
    result["Response Headers"] = headers_combined

    return result
