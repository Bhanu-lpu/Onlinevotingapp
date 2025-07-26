from flask import Flask, request, render_template, redirect, url_for, session, flash
import gspread
import pytz
import os
import requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
app.secret_key = "1644"  # Change this in production

# === Configuration ===
DEVELOPER_IP = '49.205.104.10'  # Replace with your IP
ADMIN_PASSWORD = "CodeWithBss8923"
RESULTS_RELEASED = False

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("OnlineVotingData").sheet1

# === Utility Functions ===
def has_already_voted(user_ip):
    records = sheet.get_all_records()
    return any(record.get("IP Address") == user_ip for record in records)

def get_results_flag():
    return session.get("results_released", RESULTS_RELEASED)



def get_announcements(sheet_id, sheet_name='Sheet1'):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.strip().split('\n')[1:]  # skip header
        announcements = [line.strip() for line in lines if line.strip()]
        return announcements
    except Exception as e:
        print("Error fetching announcements:", e)
        return []


# === Routes ===
@app.route('/')
def index():
    announcements = get_announcements("1cKv_LHMnINYO48JtEpuIaxR07diO1GN98XhpcKvns3Y")
    return render_template("index.html", announcements=announcements)
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    show_results = session.get("results_released", RESULTS_RELEASED) or user_ip == DEVELOPER_IP
    voted = session.get("voted", False)
    return render_template('index.html', show_results=show_results, voted=voted)

@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.form.get('party')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if not candidate:
        flash("⚠️ No candidate selected", "error")
        return redirect(url_for('index'))

    if has_already_voted(user_ip):
        flash("⚠️ You have already voted.", "error")
        return redirect(url_for('index'))

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, user_ip, candidate])
    session['voted'] = True

    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

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
    # This route simply redirects back; clearing is done via JS on the client
    return redirect(url_for('index'))

# === Run App ===
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
