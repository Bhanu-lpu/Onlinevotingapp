# # from flask import Flask, request, render_template, redirect, url_for
# # import os

# # app = Flask(__name__)

# # VOTE_FILE = 'votes.txt'
# # VOTED_IPS_FILE = 'voted_ips.txt'
# # initial_votes = {"Janasena": 0, "TDP": 0, "YSRCP": 0, "NOTA": 0}
# # RESULTS_RELEASED = False  # Change to True when you want to release results
# # ADMIN_IP = '127.0.0.1'    # Your IP address or keep as localhost
# # # Ensure the votes.txt file exists with initial votes

# # # Initialize votes.txt
# # if not os.path.exists(VOTE_FILE):
# #     with open(VOTE_FILE, 'w') as f:
# #         for party in initial_votes:
# #             f.write(f"{party}:0\n")

# # # Initialize voted_ips.txt
# # if not os.path.exists(VOTED_IPS_FILE):
# #     open(VOTED_IPS_FILE, 'w').close()

# # def get_client_ip():
# #     # If hosted behind a proxy (like in Render), check for forwarded IP
# #     return request.headers.get('X-Forwarded-For', request.remote_addr)

# # @app.route('/')
# # def index():
# #     return render_template('index.html')

# # @app.route('/vote', methods=['POST'])
# # def vote():
# #     candidate = request.form.get('candidate')
# #     client_ip = get_client_ip()

# #     if not candidate:
# #         return "No candidate selected", 400

# #     # Check if IP already voted
# #     with open(VOTED_IPS_FILE, 'r') as f:
# #         voted_ips = [ip.strip() for ip in f.readlines()]
# #     if client_ip in voted_ips:
# #         return "You have already voted from this IP address. Multiple votes are not allowed.", 403

# #     # Count the vote
# #     votes = {}
# #     with open(VOTE_FILE, 'r') as f:
# #         for line in f:
# #             name, count = line.strip().split(':')
# #             votes[name] = int(count)

# #     if candidate in votes:
# #         votes[candidate] += 1

# #     # Save updated votes
# #     with open(VOTE_FILE, 'w') as f:
# #         for name, count in votes.items():
# #             f.write(f"{name}:{count}\n")

# #     # Save IP as voted
# #     with open(VOTED_IPS_FILE, 'a') as f:
# #         f.write(f"{client_ip}\n")

# #     return redirect(url_for('results'))

# # @app.route('/results')
# # def results():
# #     user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

# #     if not RESULTS_RELEASED and user_ip != ADMIN_IP:
# #         return render_template('comingsoon.html')  # Show "Results coming soon" message

# #     votes = {}
# #     with open(VOTE_FILE, 'r') as f:
# #         for line in f:
# #             name, count = line.strip().split(':')
# #             votes[name] = int(count)

# #     return render_template('results.html', votes=votes)
# # @app.route('/admin-clear')
# # def admin_clear():
# #     if request.remote_addr != ADMIN_IP:
# #         return "Unauthorized", 403
# #     with open(VOTE_FILE, 'w') as f:
# #         for party in initial_votes:
# #             f.write(f"{party}:0\n")
# #     if os.path.exists(results):
# #         os.remove(results)
# #     return "<h2>Votes cleared by developer.</h2>"




# # if __name__ == '__main__':
# #     app.run(debug=True, port=10000)
# from flask import Flask, request, render_template, redirect, url_for
# from flask import Flask, request, render_template, redirect, url_for
# import socket
# import sqlite3

# app = Flask(__name__)
# DEVELOPER_IP = '127.0.0.1'  # Change this to your actual IP if needed
# RESULTS_RELEASED = False  # Set True when you want to show results
# developer_ip = socket.gethostbyname(socket.gethostname())

# def get_db_connection():
#     conn = sqlite3.connect('votes.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/vote', methods=['POST'])
# def vote():
#     candidate = request.form.get('candidate')
#     user_ip = request.remote_addr

#     conn = get_db_connection()
#     c = conn.cursor()

#     # Check if this IP already voted
#     c.execute("SELECT 1 FROM voters WHERE ip = ?", (user_ip,))
#     if c.fetchone():
#         conn.close()
#         return "⚠️ You have already voted. Only one vote per user is allowed."

#     # Count the vote
#     c.execute("UPDATE votes SET count = count + 1 WHERE candidate = ?", (candidate,))
#     c.execute("INSERT INTO voters (ip) VALUES (?)", (user_ip,))
#     conn.commit()
#     conn.close()

#     return redirect(url_for('results'))

# @app.route('/results')
# def results():
#     user_ip = request.remote_addr
#     if not RESULTS_RELEASED and user_ip != developer_ip:
#         return render_template('comingsoon.html')  # shows “Results will be announced soon”
    
#     # Otherwise show real results
#     votes = {}  # load from DB or file
#     return render_template('results.html', votes=votes)

# @app.route('/clear')
# def clear_votes():
#     # This only clears local user's selection (for UI, not DB)
#     return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True, port=10000)

# import sqlite3

# def get_db_connection():
#     conn = sqlite3.connect('votes.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# @app.route('/vote', methods=['POST'])
# def vote():
#     candidate = request.form.get('candidate')
#     if not candidate:
#         return "No candidate selected", 400

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("UPDATE votes SET count = count + 1 WHERE candidate = ?", (candidate,))
#     conn.commit()
#     conn.close()

#     return redirect(url_for('results'))

# @app.route('/results')
# def results():
#     user_ip = request.remote_addr
#     if not RESULTS_RELEASED and user_ip != developer_ip:
#         return render_template('results_locked.html')

#     conn = get_db_connection()
#     votes = conn.execute('SELECT * FROM votes').fetchall()
#     conn.close()
#     return render_template('results.html', votes=votes)

# @app.route('/clear')
# def clear_votes():
#     conn = get_db_connection()
#     conn.execute('UPDATE votes SET count = 0')
#     conn.commit()
#     conn.close()
#     return redirect(url_for('index'))


from flask import Flask, request, render_template, redirect, url_for
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Needed for session handling

# Now you can use `session` safely in your routes

import socket
import sqlite3

app = Flask(__name__)

# Set developer IP and control result release
DEVELOPER_IP = '127.0.0.1'  # Change this to your real IP if needed
RESULTS_RELEASED = False    # Change to True when you want to release results

# Get current system IP (for local dev)
developer_ip = '127.0.0.1'  # Because you're testing locally

# Database connection
def get_db_connection():
    conn = sqlite3.connect('votes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.form.get('candidate')
    user_ip = request.remote_addr

    if not candidate:
        return "No candidate selected", 400

    conn = get_db_connection()
    c = conn.cursor()

    # Check if the IP already voted
    c.execute("SELECT 1 FROM voters WHERE ip = ?", (user_ip,))
    if c.fetchone():
        conn.close()
        return "⚠️ You have already voted. Only one vote per user is allowed."

    # Increment vote count
    c.execute("UPDATE votes SET count = count + 1 WHERE candidate = ?", (candidate,))
    # Log voter's IP
    c.execute("INSERT INTO voters (ip) VALUES (?)", (user_ip,))
    conn.commit()
    conn.close()

    return redirect(url_for('results'))

@app.route('/results')
def results():
    user_ip = request.remote_addr
    if not RESULTS_RELEASED and user_ip != DEVELOPER_IP:
        return render_template('comingsoon.html')  # Show "Results coming soon"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM votes")
    vote_data = cursor.fetchall()
    conn.close()

    votes = {row['candidate']: row['count'] for row in vote_data}
    return render_template('results.html', votes=votes)

@app.route('/clear')
def clear_votes():
    # Only resets UI on client side — no DB change
    return redirect(url_for('index'))

# @app.route('/admin')
# def admin_dashboard():
#     user_ip = request.remote_addr
#     if user_ip != developer_ip:
#         return "⛔ Access Denied. Developer Only!"
#     ...
@app.route('/admin')
def admin_dashboard():
    user_ip = request.remote_addr
    if user_ip == developer_ip:
         # Show admin dashboard or perform admin tasks
         return render_template('admin.html')
    # If not developer, deny access
    else:
         return "⛔ Access Denied. Developer Only!"
    from flask import session

app.secret_key = 'your_secret_key'  # Add this at the top for session handling

@app.route('/admin-login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Dummy login check (replace with secure check if needed)
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        return redirect('/admin')
    else:
        return "❌ Invalid credentials", 401

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return "❌ Access Denied", 403
    return render_template('admin.html')  # Create this HTML

if __name__ == '__main__':
    app.run(debug=True, port=10000)
