from flask import Flask, render_template, request
from utils.seo_checker import analyze_seo
from utils.aio_checker import analyze_aio  # Add this import

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    meta_info_score = 0
    page_quality_score = 0
    performance_score = 0
    page_structure_score = 0
    external_score = 0
    error = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url.startswith("http"):
            url = "https://" + url

        try:
            # Get SEO data
            results = analyze_seo(url)
            
            # Get AIO data if needed
            aio_results = analyze_aio(url)
            results.update(aio_results)

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

            # --- Page Structure Score ---
            structure_checks = [
                results.get("H1 Count", 0) == 1,
                (results.get("H2 Count", 0) + results.get("H3 Count", 0)) > 1,
                results.get("Heading Hierarchy Valid", False),
                not results.get("Has Empty Links", True),
                results.get("Has Semantic Tags", False)
            ]
            page_structure_score = int((sum(structure_checks) / len(structure_checks)) * 100)

            # --- Performance Score ---
            perf_checks = [
                results.get("Page Load Time", 10) <= 2,
                results.get("HTML Size (KB)", 1000) <= 500,
                results.get("Viewport Tag") == "Present",
                results.get("Total Assets", 999) <= 100,
                "gzip" in results.get("Response Headers", "") or "zstd" in results.get("Response Headers", "")
            ]
            performance_score = int((sum(perf_checks) / len(perf_checks)) * 100)
            
            # --- External Factors Score ---
            external_checks = [
                results.get("Backlink Count", 0) > 0,
                results.get("Referring Domains", 0) > 1,
                results.get("In Authority Sources", False)
            ]
            external_score = int((sum(external_checks) / len(external_checks)) * 100)

            # Add all section scores to results
            results.setdefault("Section Scores", {})
            results["Section Scores"].update({
                "Meta Information": meta_info_score,
                "Page Quality": page_quality_score,
                "Page Structure": page_structure_score,
                "Performance": performance_score,
                "External Factors": external_score
            })

        except Exception as e:
            error = str(e)
            app.logger.error(f"Error analyzing {url}: {str(e)}")

    total_score = int((meta_info_score + page_quality_score + page_structure_score + performance_score + external_score) / 5)

    return render_template(
        "index.html",
        results=results,
        meta_info_score=meta_info_score,
        page_quality_score=page_quality_score,
        page_structure_score=page_structure_score,
        performance_score=performance_score,
        external_score=external_score,
        total_score=total_score,
        error=error
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6060, debug=True)
