from flask import Flask, render_template, request
from utils.seo_checker import analyze_seo

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    meta_info_score = 0
    page_quality_score = 0
    error = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url.startswith("http"):
            url = "https://" + url

        try:
            results = analyze_seo(url)

            # 🧠 Meta score
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

            # ✅ Page Quality score with safe .get() usage
            quality_checks = [
                results.get("Word Count", 0) >= 300,
                results.get("Has Placeholder Text", False) is False,
                results.get("Has Bullet Points", False) is True,
                results.get("Paragraph Count", 0) >= 3,
                results.get("H1 in Body Text", False) is True
            ]
            passed_quality = sum(1 for passed in quality_checks if passed)
            page_quality_score = int((passed_quality / len(quality_checks)) * 100)

            print("DEBUG Page Quality Checks:", quality_checks)

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        results=results,
        meta_info_score=meta_info_score,
        page_quality_score=page_quality_score,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)

