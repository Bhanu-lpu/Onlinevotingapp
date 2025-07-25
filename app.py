from flask import Flask, request, render_template, redirect, url_for, session, flash
import gspread
import pytz
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
app.secret_key = "1644"  # Change this in production

# ========== Configuration ==========
DEVELOPER_IP = '49.205.104.10'
ADMIN_PASSWORD = "CodeWithBss8923"
RESULTS_RELEASED = False

# ========== Google Sheets Setup ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("OnlineVotingData").sheet1

# ========== Utility Functions ==========
def load_translation(lang_code):
    path = os.path.join("translations", f"{lang_code}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    with open("translations/en.json", "r", encoding="utf-8") as fallback:
        return json.load(fallback)

def has_already_voted(user_ip):
    records = sheet.get_all_records()
    return any(record["IP Address"] == user_ip for record in records)

def get_results_flag():
    return session.get("results_released", RESULTS_RELEASED)

# ========== Routes ==========
@app.route('/')
def index():
    lang = request.args.get("lang", "en")
    session['lang'] = lang  # store user language in session
    translations = load_translation(lang)

    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    show_results = session.get("results_released", RESULTS_RELEASED) or user_ip == DEVELOPER_IP
    voted = session.get("voted", False)

    return render_template('index.html', show_results=show_results, voted=voted, t=translations, lang=lang)


@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.form.get('party')
    lang = session.get('lang', 'en')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if not candidate:
        flash("⚠️ No candidate selected", "error")
        return redirect(url_for('index', lang=lang))

    if has_already_voted(user_ip):
        flash("⚠️ You have already voted.", "error")
        return redirect(url_for('index', lang=lang))

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([now, user_ip, candidate])
    session['voted'] = True
    return redirect(url_for('thanks', lang=lang))


@app.route('/thanks')
def thanks():
    lang = session.get('lang', 'en')
    translations = load_translation(lang)
    return render_template('thanks.html', t=translations, lang=lang)


@app.route('/results')
def results():
    lang = session.get('lang', 'en')
    translations = load_translation(lang)

    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if not session.get("results_released", RESULTS_RELEASED) and user_ip != DEVELOPER_IP:
        return render_template("comingsoon.html", t=translations, lang=lang)

    records = sheet.get_all_records()
    result_count = {}

    for record in records:
        candidate = record.get("Candidate", "").strip()
        if candidate:
            result_count[candidate] = result_count.get(candidate, 0) + 1

    return render_template("results.html", votes=result_count, t=translations, lang=lang)


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    lang = session.get('lang', 'en')
    translations = load_translation(lang)

    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("❌ Incorrect password", "error")

    return render_template('admin_login.html', t=translations, lang=lang)


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    global RESULTS_RELEASED
    lang = session.get('lang', 'en')
    translations = load_translation(lang)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'release':
            RESULTS_RELEASED = True
            session['results_released'] = True
        elif action == 'hide':
            RESULTS_RELEASED = False
            session['results_released'] = False

    return render_template("admin_dashboard.html", results_released=RESULTS_RELEASED, t=translations, lang=lang)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/clear')
def clear_votes():
    return redirect(url_for('index'))

# ========== Run Server ==========
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
