from flask import Flask, request, render_template, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Configure developer IP and result control
DEVELOPER_IP = 'your.ip.address.here'  # Replace with your real IP (check it on https://whatismyipaddress.com)
RESULTS_RELEASED = False  # Change to True to allow users to see results

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("OnlineVotingData").sheet1

# Helper to check if user already voted
def has_already_voted(user_ip):
    records = sheet.get_all_records()
    return any(record["IP Address"] == user_ip for record in records)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.form.get('party')
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if party == "NOTA":
    # Save the vote to your Google Sheet or DB
    # Example:
    worksheet.append_row([ip, "NOTA", timestamp])


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
    if not RESULTS_RELEASED and user_ip != DEVELOPER_IP:
        return render_template("comingsoon.html")

    records = sheet.get_all_records()
    result_count = {}
    for record in records:
        candidate = record["Candidate"]
        result_count[candidate] = result_count.get(candidate, 0) + 1
    return render_template("results.html", votes=result_count)

@app.route('/clear')
def clear_votes():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

