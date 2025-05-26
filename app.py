from flask import Flask, render_template, request
from utils.seo_checker import analyze_seo
from utils.aio_checker import analyze_aio

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == 'POST':
        url = request.form['url']
        seo_results = analyze_seo(url)
        aio_results = analyze_aio(url)
        results = {
            'seo': seo_results,
            'aio': aio_results
        }
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)

