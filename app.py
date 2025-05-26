from flask import Flask, render_template, request
from utils.seo_checker import analyze_seo

app = Flask(__name__)
app.secret_key = "secret"

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    meta_info_score = None
    error = None

    if request.method == "POST":
        url = request.form.get("url")
        try:
            results = analyze_seo(url)

            # ✅ Meta info checklist logic
            meta_checks = [
                results['Page Title'] != 'Missing',
                results['Meta Description'] != 'Missing',
                results['robots.txt'] != 'Failed to fetch',
                False,  # Canonical URL not implemented
                results.get('Language Declared', '') != 'Missing',
                False,  # Alternate/Hreflang not implemented
                results.get('Viewport Tag') == 'Present',
                results.get('Favicon Linked') == 'Present',
                True,  # Charset assumed OK
                True,  # Domain assumed OK
                True   # URL format assumed OK
            ]
            meta_info_score = int((sum(meta_checks) / len(meta_checks)) * 100)

        except Exception as e:
            error = f"Error analyzing the site: {e}"

    return render_template("index.html", results=results, meta_info_score=meta_info_score, error=error)

if __name__ == "__main__":
    app.run(debug=True)

