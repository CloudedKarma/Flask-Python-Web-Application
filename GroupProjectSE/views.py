"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request
from GroupProjectSE import app
import os
from GroupProjectSE.ml.predict import predict_disease
from GroupProjectSE.db import get_db
from flask import request, redirect, url_for
from GroupProjectSE.db import get_db


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'MainPage.html',
        title='Project Info',
        year=datetime.now().year
    )


@app.route('/info')
def info():
    """Renders the flask page."""
    return render_template(
        'index.html',
        title='Flask Info',
        year=datetime.now().year
    )


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Name and Emails'
    )


@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='CNN Algorithm for Plant Disease Detection'
    )


# Upload folder
app.config["UPLOAD_FOLDER"] = os.path.join("GroupProjectSE", "static", "uploads")


@app.route('/plant_analysis', methods=['GET', 'POST'])
def analyze():
    result = None
    file_url = None

    if request.method == 'POST':
        file = request.files['file']

        if file.filename != "":
            filename = file.filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            file_url = "/static/uploads/" + filename

            # Run ML prediction
            result = predict_disease(save_path)

            # Save to database
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO history (image_path, predicted_class, confidence, description, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (
                file_url,
                result["class"],
                result["confidence"],
                result["description"]
            ))
            conn.commit()
            conn.close()

    return render_template(
        'plant_analysis.html',
        title='Plant Analysis',
        year=datetime.now().year,
        result=result,
        file_url=file_url
    )


@app.route('/generate_report', methods=['POST'])
def generate_report():
    file_path = request.form.get('file_path')
    result = request.form.get('result')

    return render_template(
        'report.html',
        title='Plant Analysis Report',
        year=datetime.now().year,
        file_path=file_path,
        result=result
    )


@app.route('/history', methods=['GET'])
def history():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')

    conn = get_db()
    cur = conn.cursor()

    query = "SELECT * FROM history WHERE 1=1"
    params = []

    # Search filter
    if search:
        query += " AND predicted_class LIKE ?"
        params.append(f"%{search}%")

    # Date range filter
    if start_date:
        query += " AND date(timestamp) >= date(?)"
        params.append(start_date)

    if end_date:
        query += " AND date(timestamp) <= date(?)"
        params.append(end_date)

    # Sorting options
    if sort == "newest":
        query += " ORDER BY id DESC"
    elif sort == "oldest":
        query += " ORDER BY id ASC"
    elif sort == "conf_high":
        query += " ORDER BY confidence DESC"
    elif sort == "conf_low":
        query += " ORDER BY confidence ASC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return render_template(
        "history.html",
        title="Analysis History",
        year=datetime.now().year,
        rows=rows,
        search=search,
        sort=sort,
        start=start_date,
        end=end_date
    )

@app.route('/history/delete/<int:id>', methods=['POST'])
def history_delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM history WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('history'))

@app.route('/history/view/<int:id>')
def history_view(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM history WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return render_template("error.html", message="Record not found")

    return render_template(
        "history_view.html",
        title="Full Report",
        year=datetime.now().year,
        row=row
    )

@app.route('/disease/<name>')
def disease_info(name):
    from GroupProjectSE.ml.predict import DISEASE_DATA  # load disease metadata

    if name not in DISEASE_DATA:
        return render_template("error.html", message="Disease not found")

    info = DISEASE_DATA[name]

    return render_template(
        "disease.html",
        title=f"Disease Information - {name}",
        year=datetime.now().year,
        disease=name,
        info=info
    )
