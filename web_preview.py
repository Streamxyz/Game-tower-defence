"""
Interactive Web Streamer for Pygame.
Serves a responsive canvas stream with real-time mouse clicks and keyboard controls.
"""

import os
import io
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from src.game import Game
from src.config import WINDOW_WIDTH, WINDOW_HEIGHT

game = Game()
game_lock = threading.Lock()
latest_frame = None

def game_loop_thread():
    global latest_frame
    clock = pygame.time.Clock()
    target_fps = 30
    while True:
        dt = clock.tick(target_fps) / 1000.0
        with game_lock:
            game.update(dt)
            game.draw()
            buf = io.BytesIO()
            pygame.image.save(game.screen, buf, "frame.jpg")
            latest_frame = buf.getvalue()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Modern Military Tower Defence - Live Interactive Preview</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body {
    background: #0f1316;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: 100vh;
    padding: 12px;
  }
  header {
    width: 100%;
    max-width: __WIDTH__px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: #181d22;
    border: 1px solid #2d3748;
    border-radius: 8px;
    margin-bottom: 8px;
  }
  h1 { font-size: 16px; font-weight: 700; color: #48bb78; letter-spacing: 0.5px; }
  .tagline { font-size: 12px; color: #a0aec0; }
  #game-container {
    position: relative;
    width: 100%;
    max-width: __WIDTH__px;
    background: #000;
    border: 2px solid #2b3640;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(0,0,0,0.6);
  }
  #game-view {
    width: 100%;
    height: auto;
    display: block;
    cursor: crosshair;
  }
  .controls-bar {
    margin-top: 10px;
    width: 100%;
    max-width: __WIDTH__px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
  }
  button {
    background: #2b3640;
    color: #edf2f7;
    border: 1px solid #4a5568;
    padding: 8px 14px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
  }
  button:hover { background: #3c4b58; border-color: #48bb78; }
  button.primary { background: #2f855a; border-color: #38a169; }
  button.primary:hover { background: #38a169; }
  .hint { font-size: 12px; color: #718096; margin-top: 6px; text-align: center; }
</style>
</head>
<body>
  <header>
    <div>
      <h1>MODERN MILITARY TOWER DEFENCE</h1>
      <span class="tagline">Interactive Live Stream · 1280x720 · Windows Pygame Edition</span>
    </div>
    <div>
      <span style="font-size:11px; padding: 4px 8px; background: #22543d; color: #9ae6b4; border-radius: 4px; font-weight: 600;">ACTIVE</span>
    </div>
  </header>

  <div id="game-container">
    <img id="game-view" src="/stream" alt="Game Stream" />
  </div>

  <div class="controls-bar">
    <button class="primary" onclick="sendKey(32)">Deploy Next Wave (SPACE)</button>
    <button onclick="sendKey(49)">1: Vulcan Gatling</button>
    <button onclick="sendKey(50)">2: Patriot Missile</button>
    <button onclick="sendKey(51)">3: Heavy Sniper</button>
    <button onclick="sendKey(52)">4: EMP Coil</button>
    <button onclick="sendKey(112)">Pause / Resume (P)</button>
    <button onclick="sendKey(27)">Deselect (ESC)</button>
  </div>
  <div class="hint">Click anywhere on the battlefield to place towers or inspect stats. Right-click or press ESC to cancel.</div>

<script>
  const img = document.getElementById('game-view');
  const GAME_WIDTH = __WIDTH__;
  const GAME_HEIGHT = __HEIGHT__;

  function getScaledCoords(e) {
    const rect = img.getBoundingClientRect();
    const scaleX = GAME_WIDTH / rect.width;
    const scaleY = GAME_HEIGHT / rect.height;
    const x = Math.floor((e.clientX - rect.left) * scaleX);
    const y = Math.floor((e.clientY - rect.top) * scaleY);
    return { x, y };
  }

  img.addEventListener('click', (e) => {
    const coords = getScaledCoords(e);
    fetch('/click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: coords.x, y: coords.y, button: 1 })
    }).catch(()=>{});
  });

  img.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    const coords = getScaledCoords(e);
    fetch('/click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: coords.x, y: coords.y, button: 3 })
    }).catch(()=>{});
  });

  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.code === 'Space') {
      e.preventDefault();
      sendKey(32);
    } else if (e.key === 'p' || e.key === 'P') {
      sendKey(112);
    } else if (e.key === 'Escape') {
      sendKey(27);
    } else if (['1','2','3','4'].includes(e.key)) {
      sendKey(e.key.charCodeAt(0));
    }
  });

  function sendKey(key) {
    fetch('/key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key })
    }).catch(()=>{});
  }
</script>
</body>
</html>
""".replace("__WIDTH__", str(WINDOW_WIDTH)).replace("__HEIGHT__", str(WINDOW_HEIGHT))

class WebStreamHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.send_header("Cache-Control", "no-cache, private")
            self.end_headers()
            try:
                while True:
                    frame = latest_frame
                    if frame:
                        self.wfile.write(b"--frame\r\n")
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", str(len(frame)))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b"\r\n")
                    time.sleep(0.033) # ~30 fps stream
            except (ConnectionResetError, BrokenPipeError):
                pass
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}

        if self.path == "/click":
            x = data.get("x", 0)
            y = data.get("y", 0)
            button = data.get("button", 1)
            with game_lock:
                if button == 1:
                    game.handle_click((x, y))
                elif button == 3:
                    game.selected_shop_tower = None
                    game.selected_grid_tower = None
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        elif self.path == "/key":
            key_code = data.get("key", 0)
            with game_lock:
                if key_code == 32: # SPACE
                    game.handle_keydown(pygame.K_SPACE)
                elif key_code == 112: # P
                    game.handle_keydown(pygame.K_p)
                elif key_code == 27: # ESC
                    game.handle_keydown(pygame.K_ESCAPE)
                elif key_code == 49: # 1
                    game.handle_keydown(pygame.K_1)
                elif key_code == 50: # 2
                    game.handle_keydown(pygame.K_2)
                elif key_code == 51: # 3
                    game.handle_keydown(pygame.K_3)
                elif key_code == 52: # 4
                    game.handle_keydown(pygame.K_4)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), WebStreamHandler)
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=game_loop_thread, daemon=True)
    t.start()
    run_server()
