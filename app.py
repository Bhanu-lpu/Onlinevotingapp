from flask import Flask, request, render_template, redirect, url_for, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this to a strong, secure value

# ================== Config ==================
DEVELOPER_IP = 'your.ip.address.here'  # Replace with your IP
ADMIN_PASSWORD = "CodeWithBss8923"  # Change this to your secret password
RESULTS_RELEASED = False  # Memory-stored flag (can be improved)

# ================ Google Sheets Setup ================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("OnlineVotingData").sheet1

def has_already_voted(user_ip):
    records = sheet.get_all_records()
    return any(record["IP Address"] == user_ip for record in records)

# ================= Routes =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.form.get('party')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if not candidate:
        return "⚠️ No candidate selected", 400

    if has_already_voted(user_ip):
        return "⚠️ You have already voted. Only one vote per user is allowed."

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
        candidate = record["Candidate"]
        result_count[candidate] = result_count.get(candidate, 0) + 1
    return render_template("results.html", votes=result_count)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            return "❌ Incorrect password"
    return render_template("admin_login.html")

@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    global RESULTS_RELEASED
    if request.method == 'POST':
        action = request.form.get('action')
        RESULTS_RELEASED = True if action == 'release' else False
        session['results_released'] = RESULTS_RELEASED

    return render_template("admin_panel.html", released=RESULTS_RELEASED)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/clear')
def clear_votes():
    return redirect(url_for('index'))

# ================= Server =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
