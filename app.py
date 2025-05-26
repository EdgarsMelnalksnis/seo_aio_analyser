from flask import Flask, render_template, request
from utils.seo_checker import analyze_seo

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    meta_info_score = 0
    page_quality_score = 0
    performance_score = 0
    error = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url.startswith("http"):
            url = "https://" + url

        try:
            results = analyze_seo(url)

            # --- Meta Information Score ---
            meta_checks = [
                results.get("Page Title") != "Missing",
                results.get("Meta Description") != "Missing",
                results.get("robots.txt") != "Failed to fetch",
                results.get("Language Declared", "") != "Missing",
                results.get("Viewport Tag") == "Present",
                results.get("Favicon Linked") == "Present",
                True,  # Charset encoding
                True,  # Domain format
                True,  # URL format
                False,  # Placeholder for Canonical
                False   # Placeholder for Alternate/Hreflang
            ]
            meta_info_score = int((sum(meta_checks) / len(meta_checks)) * 100)

            # --- Page Quality Score ---
            quality_checks = [
                results.get("Word Count", 0) >= 300,
                results.get("Has Placeholder Text", False) is False,
                results.get("Has Bullet Points", False) is True,
                results.get("Paragraph Count", 0) >= 3,
                results.get("H1 in Body Text", False) is True
            ]
            page_quality_score = int((sum(quality_checks) / len(quality_checks)) * 100)

            # --- Performance Score ---
            perf_checks = [
                results.get("Page Load Time", 10) <= 2,
                results.get("HTML Size (KB)", 1000) <= 500,
                results.get("Viewport Tag") == "Present",
                results.get("Total Assets", 999) <= 100,
                "gzip" in results.get("Response Headers", "") or "zstd" in results.get("Response Headers", "")
            ]
            performance_score = int((sum(perf_checks) / len(perf_checks)) * 100)
            results.setdefault("Section Scores", {})["Performance"] = performance_score
            
            print("DEBUG Performance Checks:", perf_checks)

            external_score_parts = [
                results.get("Backlink Count", 0) > 0,
                results.get("Referring Domains", 0) > 1,
                results.get("In Authority Sources", False)  # add logic later
            ]
            results["Section Scores"]["External Factors"] = int(sum(external_score_parts) / len(external_score_parts) * 100)


        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        results=results,
        meta_info_score=meta_info_score,
        page_quality_score=page_quality_score,
        performance_score=performance_score,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)

