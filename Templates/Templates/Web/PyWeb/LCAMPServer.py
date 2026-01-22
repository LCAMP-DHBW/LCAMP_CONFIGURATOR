from flask import Flask, send_from_directory, request, jsonify
import os, json, time

app = Flask(__name__)

# 1️⃣ HTML ausliefern
@app.route('/')
def serve_html():
    return send_from_directory('.', 'Configurator.html')

# 2️⃣ Andere Dateien (JS, JSON) ausliefern
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# 3️⃣ JSON auf Server speichern
SAVE_FOLDER = "saved_configs"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route('/save_json', methods=['POST'])
def save_json():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine JSON-Daten"}), 400
    print(data)
    filename = f"RobotConfig_{int(time.time())}.json"
    filepath = os.path.join(SAVE_FOLDER, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

 #   filename = f"RobotConfig.json"
 #   filepath = os.path.join(SAVE_FOLDER, filename)
 #   with open(filepath, 'w', encoding='utf-8') as f:
 #       json.dump(data, f, indent=2)

    return jsonify({"message": "Datei gespeichert", "file": filename})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

