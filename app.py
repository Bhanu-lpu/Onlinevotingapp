from flask import Flask, request, render_template, redirect, url_for, session, flash
import gspread
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

def has_already_voted(user_ip):
    records = sheet.get_all_records()
    return any(record["IP Address"] == user_ip for record in records)

def get_results_flag():
    return session.get("results_released", RESULTS_RELEASED)

# ========== Routes ==========

@app.route('/')
def index():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    show_results = get_results_flag() or user_ip == DEVELOPER_IP
    return render_template('index.html', show_results=show_results)

@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.form.get('party')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if not candidate:
        return "⚠️ No candidate selected", 400

    if has_already_voted(user_ip):
        return "⚠️ You have already voted."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, user_ip, candidate])
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return "✅ Thank you for voting!"

@app.route('/results')
def results():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if not session.get("results_released", RESULTS_RELEASED) and user_ip != DEVELOPER_IP:
        return render_template("comingsoon.html")

    records = sheet.get_all_records()
    result_count = {}

    for record in records:
        candidate = record.get("Candidate", "").strip()
        if candidate:
            result_count[candidate] = result_count.get(candidate, 0) + 1

    return render_template("results.html", votes=result_count)


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("❌ Incorrect password", "error")
    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    global RESULTS_RELEASED
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'release':
            RESULTS_RELEASED = True
            session['results_released'] = True
        elif action == 'hide':
            RESULTS_RELEASED = False
            session['results_released'] = False

    return render_template("admin_dashboard.html", results_released=RESULTS_RELEASED)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/clear')
def clear_votes():
    return redirect(url_for('index'))

# ========== Server ==========
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
