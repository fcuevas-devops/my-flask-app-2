import os
import requests
import json 
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
        return {'temp': data["current_weather"]['temperature'], 'viento': data['current_weather']['windspeed']}
    except Exception as e:
        return {"error": str(e)},500

def obtener_clima2():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {'latitude': 40.4168, 'longitude': -3.7038, 'current_weather': True}
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        return data
    except Exception as e:
        return {"error": str(e)},500



def obtener_clima3(lat=40.4168, lon=-3.7038):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }
    
    print(f"🌍 Llamando a Open-Meteo para: {lat}, {lon}") # Log para depurar
    
    try:
        response = requests.get(url, params=params, timeout=5)
        
        # Imprimir el código de estado y el texto crudo para ver el error real
        print(f"Estado HTTP: {response.status_code}")
        print(f"Respuesta cruda: {response.text[:200]}") # Imprime los primeros 200 caracteres
        
        response.raise_for_status() # Lanza error si el status es 4xx o 5xx
        
        data = response.json()
        current = data['current_weather']
        
        return {
            "latitud": lat,
            "longitud": lon,
            "temperatura": current['temperature'],
            "viento": current['windspeed'],
            "hora": current['time']
        }
    except requests.exceptions.Timeout:
        return {"error": "Timeout: La API de Open-Meteo no respondió a tiempo."}
    except requests.exceptions.RequestException as e:
        # Aquí capturamos el error real de la red
        return {"error": f"Error de red: {str(e)}", "detalles": response.text if 'response' in locals() else "Sin respuesta"}
    except KeyError as e:
        # Si la estructura de la respuesta de Open-Meteo cambió o no tiene 'current_weather'
        return {"error": "Error de formato en la respuesta de Open-Meteo", "clave_faltante": str(e)}
    

@app.route('/clima')
def ver_clima():
    return jsonify(obtener_clima())

@app.route('/clima2')
def ver_clima2():
    return jsonify(obtener_clima2())

@app.route('/clima3')
def ver_clima3():
    return jsonify(obtener_clima3())

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
