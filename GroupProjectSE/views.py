"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from GroupProjectSE import app
import os
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from GroupProjectSE.auth import get_user_by_username, User
from GroupProjectSE.db import get_db
from GroupProjectSE.ml.predict import predict_disease, DISEASE_DATA
import csv
from flask import make_response
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter



@app.route('/')
@app.route('/home')
def home():
    return render_template('MainPage.html', title='Project Info', year=datetime.now().year)


@app.route('/info')
def info():
    return render_template('index.html', title='Flask Info', year=datetime.now().year)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact', year=datetime.now().year)


@app.route('/about')
def about():
    return render_template('about.html', title='About', year=datetime.now().year)


# Upload folder
app.config["UPLOAD_FOLDER"] = os.path.join("GroupProjectSE", "static", "uploads")


# -------------------- REGISTER --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed, role)
            )
            conn.commit()
        except:
            flash("Username already exists.")
            return redirect(url_for('register'))
        finally:
            conn.close()

        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))

    return render_template("register.html")


# -------------------- LOGIN --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_username(username)

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.")

    return render_template('login.html')


# -------------------- LOGOUT --------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# -------------------- PROFILE --------------------
@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)


# -------------------- PLANT ANALYSIS --------------------
@app.route('/plant_analysis', methods=['GET', 'POST'])
@login_required
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
                INSERT INTO history (user_id, image_path, predicted_class, confidence, description, timestamp)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (
                current_user.id,
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


# -------------------- REPORT GENERATION --------------------
@app.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    file_path = request.form.get('file_path') or request.args.get('file_path')
    result = request.form.get('result') or request.args.get('result')

    return render_template(
        'report.html',
        title='Plant Analysis Report',
        year=datetime.now().year,
        file_path=file_path,
        result=result
    )


# -------------------- HISTORY --------------------
@app.route('/history', methods=['GET'])
@login_required
def history():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')

    conn = get_db()
    cur = conn.cursor()

    # Instructor sees all
    # Student sees only their own
    if current_user.role == "student":
        query = "SELECT * FROM history WHERE user_id = ?"
        params = [current_user.id]
    else:
        query = "SELECT * FROM history WHERE 1=1"
        params = []

    # Filters
    if search:
        query += " AND predicted_class LIKE ?"
        params.append(f"%{search}%")

    if start_date:
        query += " AND date(timestamp) >= date(?)"
        params.append(start_date)

    if end_date:
        query += " AND date(timestamp) <= date(?)"
        params.append(end_date)

    # Sorting
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
@login_required
def history_delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM history WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('history'))


@app.route('/history/view/<int:id>')
@login_required
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


# -------------------- DISEASE INFO --------------------
@app.route('/disease/<name>')
def disease_info(name):
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
# -------------------- MODEL INFO --------------------
@app.route('/model_info')
def model_info():
    import json
    
    base_dir = os.path.dirname(os.path.abspath(__file__))  # folder of views.py
    info_path = os.path.join(base_dir, "ml", "model_info.json")

    with open(info_path, "r") as f:
        data = json.load(f)

    return render_template(
        "model_info.html",
        title="Model Information",
        year=datetime.now().year,
        data=data
    )

# -------------------- CSV DOWNLOAD INFO --------------------

@app.route('/history/download/csv')
@login_required
def download_history_csv():
    conn = get_db()
    cur = conn.cursor()

    # Instructor = all records; Student = only their own
    if current_user.role == "student":
        cur.execute("SELECT * FROM history WHERE user_id = ? ORDER BY id DESC",
                    (current_user.id,))
    else:
        cur.execute("SELECT * FROM history ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()

    # Create CSV in memory
    response = make_response()
    response.headers["Content-Disposition"] = "attachment; filename=history.csv"
    response.headers["Content-Type"] = "text/csv"

    writer = csv.writer(response)
    writer.writerow(["ID", "Image", "Disease", "Confidence", "Description", "Timestamp"])

    for row in rows:
        writer.writerow([
            row["id"],
            row["image_path"],
            row["predicted_class"],
            row["confidence"],
            row["description"],
            row["timestamp"]
        ])

    return response

# -------------------- DOWNLOAD PDF INFO --------------------

@app.route('/history/download/pdf')
@login_required
def download_history_pdf():
    conn = get_db()
    cur = conn.cursor()

    if current_user.role == "student":
        cur.execute("SELECT * FROM history WHERE user_id = ? ORDER BY id DESC",
                    (current_user.id,))
    else:
        cur.execute("SELECT * FROM history ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()

    pdf_path = "history_report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    title = Paragraph("Plant Analysis History Report", styles["Title"])
    content.append(title)
    content.append(Spacer(1, 20))

    for row in rows:
        # Each entry formatted
        text = (
            f"<b>ID:</b> {row['id']}<br/>"
            f"<b>Disease:</b> {row['predicted_class']}<br/>"
            f"<b>Confidence:</b> {row['confidence']}%<br/>"
            f"<b>Description:</b> {row['description']}<br/>"
            f"<b>Date:</b> {row['timestamp']}<br/><br/>"
        )
        content.append(Paragraph(text, styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="Plant_History_Report.pdf"
    )