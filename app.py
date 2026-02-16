from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os
import traceback

# Flaskアプリの初期化
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dcs-obs-controller-secret-key'
CORS(app)

# SocketIOの初期化
socketio = SocketIO(app, 
                    cors_allowed_origins="*",
                    async_mode='threading',
                    logger=True,
                    engineio_logger=True)

# 設定ファイルのパス
CONFIG_FILE = 'config.json'

# デフォルト設定
DEFAULT_CONFIG = {
    "modes": [
        {
            "id": "dcs_basic",
            "name": "DCS基本操作",
            "buttons": [
                {"name": "ギア", "key": "g", "color": "blue"},
                {"name": "フラップ", "key": "f", "color": "blue"},
                {"name": "エアブレーキ", "key": "b", "color": "orange"},
                {"name": "ライト", "key": "l", "color": "green"}
            ]
        },
        {
            "id": "obs_control",
            "name": "OBS制御",
            "buttons": [
                {"name": "録画開始/停止", "key": "F13", "color": "red"},
                {"name": "配信開始/停止", "key": "F14", "color": "red"},
                {"name": "シーン1", "key": "F15", "color": "blue"},
                {"name": "シーン2", "key": "F16", "color": "blue"}
            ]
        }
    ]
}

# 設定の読み込み
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content:
                    return DEFAULT_CONFIG
                return json.loads(content)
        except Exception as e:
            print(f"[ERROR] 設定ファイルの読み込みに失敗: {e}")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

# 設定の保存
def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 設定を {CONFIG_FILE} に保存しました。")
        return True
    except Exception as e:
        print(f"[ERROR] 設定ファイルの保存に失敗: {e}")
        traceback.print_exc()
        return False

# キーボード制御（変更なし）
class KeyController:
    def __init__(self):
        self.keyboard = None; self.use_keyboard = False
        try:
            import keyboard; self.keyboard = keyboard; self.use_keyboard = True; print("[INFO] Using 'keyboard' library")
        except ImportError:
            try:
                from pynput.keyboard import Controller, Key; self.keyboard = Controller(); self.Key = Key; self.use_keyboard = False; print("[INFO] Using 'pynput' library")
            except ImportError:
                print("[ERROR] Neither 'keyboard' nor 'pynput' is installed!"); self.keyboard = None
    def press_key(self, key_string):
        if not self.keyboard: return False, "Keyboard library not available"
        try:
            if self.use_keyboard: self.keyboard.press_and_release(key_string)
            else: self._press_key_pynput(key_string)
            return True, f"Key '{key_string}' pressed"
        except Exception as e: return False, str(e)
    def _press_key_pynput(self, key_string):
        keys = key_string.lower().split('+'); modifier_map = {'ctrl': self.Key.ctrl, 'shift': self.Key.shift, 'alt': self.Key.alt, 'cmd': self.Key.cmd, 'win': self.Key.cmd}; special_keys = {'space': self.Key.space, 'enter': self.Key.enter, 'tab': self.Key.tab, 'esc': self.Key.esc, 'backspace': self.Key.backspace, 'delete': self.Key.delete, 'up': self.Key.up, 'down': self.Key.down, 'left': self.Key.left, 'right': self.Key.right};
        for i in range(1, 25): special_keys[f'f{i}'] = getattr(self.Key, f'f{i}')
        modifiers = []; main_key = None
        for key in keys:
            key = key.strip()
            if key in modifier_map: modifiers.append(modifier_map[key])
            else: main_key = key
        for mod in modifiers: self.keyboard.press(mod)
        if main_key:
            if main_key in special_keys: self.keyboard.press(special_keys[main_key]); self.keyboard.release(special_keys[main_key])
            else: self.keyboard.press(main_key); self.keyboard.release(main_key)
        for mod in reversed(modifiers): self.keyboard.release(mod)
key_controller = KeyController()

@app.route('/')
def index():
    return render_template('mobile.html')

@app.route('/pc')
def pc():
    return render_template('pc.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(load_config())

# --- ▼ 修正点 ▼ ---
# socketio.emit から broadcast=True を削除
@app.route('/api/config', methods=['POST'])
def update_config():
    config = request.json

    # --- ▼ ここからが追加する処理 ▼ ---
    # PC画面(label)とスマホ画面(name)のキー名の違いを吸収する
    for mode in config.get('modes', []):
        for button in mode.get('buttons', []):
            if 'label' in button:
                button['name'] = button.pop('label')
    # --- ▲ 追加処理はここまで ▲ ---

    if save_config(config):
        # 成功した場合
        socketio.emit('config_update', config)
        return jsonify({"success": True, "message": "設定を保存しました。"})
    else:
        # 失敗した場合
        return jsonify({"success": False, "message": "エラー: 設定ファイルの保存に失敗しました。"}), 500

# SocketIOイベントハンドラ
@socketio.on('connect')
def handle_connect():
    print(f"[SOCKET] Client connected: {request.sid}")
    emit('config_update', load_config())

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[SOCKET] Client disconnected: {request.sid}")

@socketio.on('request_config')
def handle_request_config():
    emit('config_update', load_config())

@socketio.on('send_key')
def handle_send_key(data):
    key = data.get('key', '')
    print(f"[KEY] Pressing: {key}")
    success, message = key_controller.press_key(key)
    emit('key_result', {'success': success, 'key': key, 'message': message})

if __name__ == '__main__':
    print("=" * 50)
    print("DCS/OBS Controller Server")
    print("=" * 50)
    print("PC用設定画面: http://localhost:5000/pc")
    print("スマホ用画面: http://[PCのIP]:5000/")
    print("=" * 50)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
