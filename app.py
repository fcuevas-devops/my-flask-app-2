import os
import requests
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

# Conectar a DB (Render inyecta DATABASE_URL automáticamente)
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        return None
    return psycopg2.connect(db_url, sslmode='require')

# Capa Externa: API de Clima
def obtener_clima():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {'latitude': 40.4168, 'longitude': -3.7038, 'current_weather': True}
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        return {'temp': data['current_weather']['temperature'], 'viento': data['current_weather']['windspeed']}
    except:
        return {'error': 'Fallo API'}

@app.route('/clima')
def ver_clima():
    return jsonify(obtener_clima())

@app.route('/guardar', methods=['POST'])
def guardar():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Sin DB"}), 503
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS demo (mensaje TEXT)")
        cur.execute("INSERT INTO demo (mensaje) VALUES (%s)", ("Dato de prueba",))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "Guardado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)