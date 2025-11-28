from flask import Flask, render_template_string, jsonify, send_from_directory, g, request, Response
from datetime import datetime, timedelta
import threading
import os

app = Flask(__name__)

active_users = {}           
peak_today = 0              
lock = threading.Lock()     

def cleanup_old_sessions():
    with lock:
        now = datetime.utcnow()
        expired = [ip for ip, ts in active_users.items() if now - ts > timedelta(minutes=2)]
        for ip in expired:
            del active_users[ip]

def start_cleanup_task():
    def run():
        while True:
            cleanup_old_sessions()
            threading.Event().wait(300)  
    threading.Thread(target=run, daemon=True).start()

start_cleanup_task()

@app.before_request
def track_visitor():

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip:
        ip = ip.split(',')[0].strip()

    now = datetime.utcnow()
    with lock:
        was_already_active = ip in active_users
        active_users[ip] = now

        current_count = len(active_users)

        g.current_viewers = current_count

        global peak_today
        if current_count > peak_today:
            peak_today = current_count
            app.peak_today = peak_today  

@app.before_request
def reset_peak_if_new_day():
    today = datetime.utcnow().date()
    if not hasattr(app, 'peak_date') or app.peak_date != today:
        global peak_today
        peak_today = len(active_users)
        app.peak_today = peak_today
        app.peak_date = today

studio_info = {
    "name": "Hunterz Studios",
    "description": "Made by two passionate young game developers",
    "email": "studios.hunterz@gmail.com",
    "game_email": "forcedentry.game@gmail.com",
    "website": "https://forcedentry.netlify.app/"
}

games = [
    {
        "title": "Forced Entry",
        "description": "An intense action experience that challenges players with strategic combat and immersive environments.",
        "link": "https://forcedentry.netlify.app/",
        "status": "In Development"
    }
]

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    return render_template_string(html_content, studio=studio_info, games=games)

@app.route('/api/studio')
def get_studio_info():
    return jsonify(studio_info)

@app.route('/api/games')
def get_games():
    return jsonify(games)

@app.route('/api/viewers')
def get_current_viewers():
    count = getattr(g, 'current_viewers', len(active_users))
    return jsonify({
        "online-now": count,
        "peak_today": getattr(app, 'peak-today', count)
    })

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
