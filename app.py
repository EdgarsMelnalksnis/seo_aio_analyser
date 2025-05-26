from flask import Flask, render_template, request

from utils.seo_checker import analyze_seo  # You must have this script with analyze_seo()

app = Flask(__name__)
app.secret_key = "secret"

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    if request.method == "POST":
        url = request.form.get("url")
        results = analyze_seo(url)
        if "error" in results:
            error = results["error"]
            results = None
    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True)
