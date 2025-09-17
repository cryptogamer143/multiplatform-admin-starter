# Minimal Flask backend for Multi-Platform Admin Starter
import os
import sqlite3
from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import uuid
import json

DB_PATH = os.environ.get('MP_DB', 'data.db')

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY,
                    platform TEXT,
                    account_name TEXT,
                    access_token TEXT,
                    refresh_token TEXT,
                    meta JSON
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    media_url TEXT,
                    platforms JSON,
                    schedule_at TEXT,
                    status TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

# Simple scheduler that looks for scheduled posts and "publishes" them
scheduler = BackgroundScheduler()

def publish_due_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("SELECT id, content, media_url, platforms FROM posts WHERE schedule_at <= ? AND status = ?", (now, 'scheduled'))
    rows = c.fetchall()
    for row in rows:
        post_id, content, media_url, platforms_json = row
        platforms = json.loads(platforms_json)
        # Placeholder: here you would call each platform's API using stored tokens
        print(f"Publishing {post_id} to {platforms}")
        # Mark as published
        c.execute("UPDATE posts SET status = ? WHERE id = ?", ('published', post_id))
    conn.commit()
    conn.close()

scheduler.add_job(publish_due_posts, 'interval', seconds=30)
scheduler.start()

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.utcnow().isoformat()})

# --- Accounts endpoints (connect / list) ---
@app.route('/accounts', methods=['GET'])
def list_accounts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, platform, account_name, meta FROM accounts")
    rows = c.fetchall()
    conn.close()
    accounts = [{'id': r[0], 'platform': r[1], 'account_name': r[2], 'meta': json.loads(r[3]) if r[3] else {}} for r in rows]
    return jsonify(accounts)

@app.route('/accounts/connect/<platform>', methods=['GET'])
def connect_platform(platform):
    # Redirect user to the real OAuth consent page for the chosen platform.
    # For the starter, we'll return a placeholder URL and then a dummy token exchange route.
    # Replace these URLs with actual OAuth URLs for each platform.
    dummy_oauth_url = url_for('oauth_callback', platform=platform, _external=True) + "?code=demo_code"
    return redirect(dummy_oauth_url)

@app.route('/oauth/callback/<platform>', methods=['GET'])
def oauth_callback(platform):
    # In real usage you'd receive `code` and exchange it for tokens.
    code = request.args.get('code')
    # Placeholder: perform token exchange here using 'code'
    # Save dummy account
    acc_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    meta = json.dumps({'connected_at': datetime.utcnow().isoformat(), 'demo_code': code})
    c.execute("INSERT INTO accounts (id, platform, account_name, access_token, refresh_token, meta) VALUES (?, ?, ?, ?, ?, ?)",
              (acc_id, platform, platform + '_demo_account', 'demo_access_token', 'demo_refresh', meta))
    conn.commit()
    conn.close()
    return jsonify({'status': 'connected', 'platform': platform, 'account_id': acc_id})

# --- Content endpoints ---
@app.route('/content/create', methods=['POST'])
def create_content():
    data = request.json
    content = data.get('content', '')
    media_url = data.get('media_url', '')
    platforms = data.get('platforms', ['instagram'])
    schedule_at = data.get('schedule_at')  # ISO datetime string in UTC or None for immediate
    post_id = str(uuid.uuid4())
    status = 'scheduled' if schedule_at else 'published'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO posts (id, content, media_url, platforms, schedule_at, status) VALUES (?, ?, ?, ?, ?, ?)",
              (post_id, content, media_url, json.dumps(platforms), schedule_at if schedule_at else datetime.utcnow().isoformat(), status))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'post_id': post_id})

@app.route('/content/list', methods=['GET'])
def list_content():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, content, media_url, platforms, schedule_at, status FROM posts ORDER BY schedule_at DESC")
    rows = c.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'id': r[0],
            'content': r[1],
            'media_url': r[2],
            'platforms': json.loads(r[3]),
            'schedule_at': r[4],
            'status': r[5]
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
