from flask import Flask, request, render_template, redirect, url_for, session, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "1644"  # Change this in production

# ========== Configuration ==========
DEVELOPER_IP = '49.205.104.10'
ADMIN_PASSWORD = "CodeWithBss8923"
RESULT_FLAG_FILE = "result_flag.txt"

# ========== Google Sheets Setup ==========
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("OnlineVotingData").sheet1

# ========== Utility Functions ==========
def has_already_voted(user_ip):
    records = sheet.get_all_records()
    return any(record["IP Address"] == user_ip for record in records)

def is_result_released():
    return os.path.exists(RESULT_FLAG_FILE)

def set_result_release(status):
    if status:
        open(RESULT_FLAG_FILE, 'w').close()
    elif os.path.exists(RESULT_FLAG_FILE):
        os.remove(RESULT_FLAG_FILE)

# ========== Routes ==========
@app.route('/')
def index():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    show_results = is_result_released() or user_ip == DEVELOPER_IP
    return render_template('index.html', show_results=show_results)

@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.form.get('party')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if not candidate:
        return "\u26a0\ufe0f No candidate selected", 400

    if has_already_voted(user_ip):
        return "\u26a0\ufe0f You have already voted."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, user_ip, candidate])
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return "\u2705 Thank you for voting!"
@app.route('/results')
def results():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if not get_results_flag() and user_ip != DEVELOPER_IP:
        return render_template("comingsoon.html")

    allowed_candidates = ["TDP", "JSP", "YSRCP", "NOTA"]
    records = sheet.get_all_records()
    result_count = {c: 0 for c in allowed_candidates}

    for record in records:
        candidate = record.get("Candidate", "").strip()
        if candidate in allowed_candidates:
            result_count[candidate] += 1

    return render_template("results.html", votes=result_count)


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("\u274c Incorrect password", "error")
    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'release':
            set_result_release(True)
        elif action == 'hide':
            set_result_release(False)

    return render_template("admin_dashboard.html", results_released=is_result_released())

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
