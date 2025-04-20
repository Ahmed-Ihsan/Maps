# app.py (Flask backend)
from flask import Flask, render_template, request, jsonify
import requests
from ipaddress import ip_address, AddressValueError
import time
from threading import Lock

app = Flask(__name__)
lock = Lock()
geolocation_data = []
MAX_HISTORY = 50

class NordVPNLookup:
    API_URL = "https://web-api.nordvpn.com/v1/ips/lookup/{ip}"
    
    @classmethod
    def get_location(cls, ip):
        try:
            response = requests.get(cls.API_URL.format(ip=ip), timeout=10)
            response.raise_for_status()
            data = response.json()
            print(data)
            if 'ip' not in data:
                return None
            
            return {
                'ip': data['ip'],
                'city': data.get('city', 'N/A'),
                'region': data.get('region', 'N/A'),
                'country': data.get('country_name', 'N/A'),
                'country_code': data.get('country_code', 'N/A'),
                'isp': data.get('org', 'N/A'),
                'lat': data.get('latitude'),
                'lon': data.get('longitude'),
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"Error processing {ip}: {str(e)}")
            return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_ip():
    ip = request.form.get('ip').strip()
    
    # Validate IP address
    try:
        ip_address(ip)
    except AddressValueError:
        return jsonify({'error': 'Invalid IP format'}), 400
    
    # Check if already processed recently
    existing = next((item for item in geolocation_data if item['ip'] == ip), None)
    if existing and (time.time() - existing['timestamp']) < 3600:
        return jsonify({'message': 'IP already processed recently'}), 200
    
    # Perform geolocation lookup
    with lock:
        location = NordVPNLookup.get_location(ip)
        if location:
            geolocation_data.append(location)
            # Keep only recent entries
            if len(geolocation_data) > MAX_HISTORY:
                geolocation_data.pop(0)
            return jsonify(location)
        else:
            return jsonify({'error': 'Geolocation failed'}), 500

@app.route('/data')
def get_data():
    return jsonify(geolocation_data)

if __name__ == '__main__':
    app.run(debug=True,port=3000, threaded=True)