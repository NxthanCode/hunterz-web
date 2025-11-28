from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

studio_info = {
    "name": "Hunterz Studios",
    "description": "Made by two passionate 16-year-old game developers",
    "email": "studios.hunterz@gmail.com",
    "game_email": "forcedentry.game@gmail.com",
    "website": "https://forcedentry.netlify.app/"
}

games = [
    {
        "title": "ForceD Entry",
        "description": "Our flagship game - an exciting action experience",
        "link": "https://forcedentry.netlify.app/",
        "status": "In Development"
    }
]

@app.route('/')
def index():
    return render_template('index.html', studio=studio_info, games=games)

@app.route('/api/studio')
def get_studio_info():
    return jsonify(studio_info)

@app.route('/api/games')
def get_games():
    return jsonify(games)

if __name__ == '__main__':

    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)


    app.run(debug=True, host='0.0.0.0', port=5000)