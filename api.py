"""
Minecraft Launcher API для Railway
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
import hashlib
import hmac
import base64
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с любых доменов

# Секретный ключ (лучше задать через переменные окружения Railway)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Базовая директория
BASE_DIR = Path(__file__).parent

def encrypt_response(data):
    """Шифрование ответа"""
    json_str = json.dumps(data, ensure_ascii=False)
    signature = hmac.new(
        SECRET_KEY.encode(),
        json_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'data': base64.b64encode(json_str.encode()).decode(),
        'signature': signature,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/')
def index():
    """Главная страница (проверка что API работает)"""
    return jsonify({
        'status': 'online',
        'server': 'Minecraft Launcher API',
        'railway': True
    })

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'online',
        'time': datetime.now().isoformat()
    })

@app.route('/api/config')
def get_config():
    try:
        with open(BASE_DIR / 'config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(encrypt_response(config))
    except:
        return jsonify({'error': 'Config not found'}), 404

@app.route('/api/news')
def get_news():
    try:
        with open(BASE_DIR / 'news.json', 'r', encoding='utf-8') as f:
            news = json.load(f)
        return jsonify(encrypt_response(news))
    except:
        return jsonify([])

@app.route('/api/versions')
def get_versions():
    try:
        with open(BASE_DIR / 'versions.json', 'r', encoding='utf-8') as f:
            versions = json.load(f)
        return jsonify(encrypt_response(versions))
    except:
        return jsonify({})

@app.route('/api/mods')
def get_mods():
    try:
        with open(BASE_DIR / 'mods.json', 'r', encoding='utf-8') as f:
            mods = json.load(f)
        return jsonify(encrypt_response(mods))
    except:
        return jsonify([])

@app.route('/api/builds')
def get_builds():
    try:
        with open(BASE_DIR / 'builds.json', 'r', encoding='utf-8') as f:
            builds = json.load(f)
        return jsonify(encrypt_response(builds))
    except:
        return jsonify([])

@app.route('/api/download/mod/<mod_id>')
def download_mod(mod_id):
    """Скачать мод"""
    mod_path = BASE_DIR / 'downloads' / 'mods' / f"{mod_id}.jar"
    if mod_path.exists():
        return send_file(mod_path, as_attachment=True)
    return jsonify({'error': 'Mod not found'}), 404

@app.route('/api/download/build/<build_name>')
def download_build(build_name):
    """Скачать сборку"""
    build_path = BASE_DIR / 'downloads' / 'builds' / f"{build_name}.zip"
    if build_path.exists():
        return send_file(build_path, as_attachment=True)
    return jsonify({'error': 'Build not found'}), 404

@app.route('/api/check_update', methods=['POST'])
def check_update():
    """Проверка обновлений"""
    data = request.json
    current_version = data.get('version', '1.0.0')
    
    try:
        with open(BASE_DIR / 'updates.json', 'r', encoding='utf-8') as f:
            updates = json.load(f)
        
        if updates.get('latest_version', '1.0.0') > current_version:
            return jsonify({
                'update_available': True,
                'latest_version': updates['latest_version'],
                'download_url': f"/api/download/update/{updates['latest_version']}",
                'changelog': updates.get('changelog', [])
            })
    except:
        pass
    
    return jsonify({'update_available': False})

@app.route('/api/download/update/<version>')
def download_update(version):
    """Скачать обновление лаунчера"""
    update_path = BASE_DIR / 'downloads' / 'updates' / f"launcher_v{version}.exe"
    if update_path.exists():
        return send_file(update_path, as_attachment=True)
    return jsonify({'error': 'Update not found'}), 404

@app.route('/api/stats', methods=['POST'])
def collect_stats():
    """Сбор статистики"""
    data = request.json
    stats_file = BASE_DIR / 'logs' / 'stats.json'
    
    try:
        stats_file.parent.mkdir(exist_ok=True)
        
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {'launches': []}
        
        stats['launches'].append({
            'timestamp': datetime.now().isoformat(),
            'username': data.get('username'),
            'version': data.get('version'),
            'ram': data.get('ram')
        })
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return jsonify({'success': True})
    except:
        return jsonify({'error': 'Stats error'}), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Обратная связь"""
    data = request.json
    feedback_file = BASE_DIR / 'logs' / 'feedback.json'
    
    try:
        feedback_file.parent.mkdir(exist_ok=True)
        
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                feedbacks = json.load(f)
        else:
            feedbacks = []
        
        feedbacks.append({
            'timestamp': datetime.now().isoformat(),
            'username': data.get('username'),
            'message': data.get('message'),
            'rating': data.get('rating')
        })
        
        with open(feedback_file, 'w') as f:
            json.dump(feedbacks, f, indent=2)
        
        return jsonify({'success': True})
    except:
        return jsonify({'error': 'Feedback error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)