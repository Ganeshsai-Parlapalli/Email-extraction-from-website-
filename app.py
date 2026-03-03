from flask import Flask, render_template, request, jsonify, send_file
from scraper.directory_scraper import scrape_directory
import pandas as pd
import os
import sys
import webbrowser
import threading

# Fix template path for EXE
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

app = Flask(__name__, template_folder=os.path.join(base_path, "templates"))

@app.route("/")
def home():
    return render_template("index.html", total=0)

@app.route("/start", methods=["POST"])
def start_scraping():
    try:
        data = request.json
        url = data.get("url")

        if not url:
            return jsonify({
                "message": "Please enter a URL."
            })

        results = scrape_directory(url)

        if not results:
            return jsonify({
                "message": "No emails found.",
                "total": 0
            })

        df = pd.DataFrame(results)

        file_path = os.path.join(base_path, "emails.xlsx")
        df.to_excel(file_path, index=False)

        return jsonify({
            "message": f"Extraction completed. {len(results)} emails found.",
            "total": len(results)
        })

    except Exception as e:
        return jsonify({
            "message": f"Error occurred: {str(e)}"
        })

@app.route("/download/excel")
def download_excel():
    file_path = os.path.join(base_path, "emails.xlsx")
    return send_file(file_path, as_attachment=True)

@app.route("/download/csv")
def download_csv():
    excel_path = os.path.join(base_path, "emails.xlsx")
    df = pd.read_excel(excel_path)
    csv_path = os.path.join(base_path, "emails.csv")
    df.to_csv(csv_path, index=False)
    return send_file(csv_path, as_attachment=True)

# Auto-open browser when EXE runs
def open_browser():
    webbrowser.open("http://127.0.0.1:5050")

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(host="127.0.0.1", port=5050, debug=False)