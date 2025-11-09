# keepalive.py - Keeps bot running on WispByte/Pterodactyl hosting
# Place this file in the same directory as bot.py

from flask import Flask
from threading import Thread
import time
import requests
import logging

# Suppress Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Discord Mod Bot - Status</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #2c2f33;
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: #23272a;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
            }
            .status {
                font-size: 48px;
                color: #43b581;
                margin-bottom: 20px;
            }
            .info {
                font-size: 18px;
                color: #99aab5;
            }
            .pulse {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status pulse">✅ ONLINE</div>
            <h1>Discord Moderation Bot</h1>
            <p class="info">Bot is running and healthy</p>
            <p class="info">Auto-refreshing every 30 seconds</p>
        </div>
    </body>
    </html>
    """

@app.route('/ping')
def ping():
    return {'status': 'alive', 'timestamp': time.time()}

@app.route('/health')
def health():
    return {'status': 'healthy', 'uptime': time.time()}

def run():
    """Run Flask server"""
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Start Flask server in background thread"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("✅ Keepalive server started on port 8080")

def self_ping():
    """Self-ping to prevent idling (optional)"""
    while True:
        time.sleep(300)  # Every 5 minutes
        try:
            requests.get('http://localhost:8080/ping', timeout=5)
            print("🔄 Self-ping successful")
        except:
            pass

def start_self_ping():
    """Start self-ping in background thread"""
    t = Thread(target=self_ping)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    keep_alive()
    print("Keepalive server running...")
    print("Visit http://your-server-ip:8080 to check status")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
