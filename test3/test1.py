from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import time
import json
import threading
import sys
import ipaddress
import requests

class IPStreamHandler(BaseHTTPRequestHandler):
    clients = []
    
    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.clients.append(self.wfile)
            return
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(self.generate_interface().encode('utf-8'))
            return

    def generate_interface(self):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Live IP Geolocation</title>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #0F172A; color: #E5E7EB; }}
                .container {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; padding: 20px; }}
                #map {{ height: 80vh; border: 1px solid #374151; border-radius: 8px; }}
                #table {{ overflow-y: auto; max-height: 80vh; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #374151; }}
                th {{ background: #1E293B; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div id="map"></div>
                <div id="table"></div>
            </div>
            <script>
                const eventSource = new EventSource('/stream');
                const tableDiv = document.getElementById('table');
                let map;

                function initMap() {{
                    map = new google.maps.Map(document.getElementById('map'), {{
                        center: {{lat: 0, lng: 0}},
                        zoom: 2,
                        styles: [
                            {{ elementType: "geometry", stylers: [{{ color: "#1E293B" }}] }},
                            {{ elementType: "labels.text.stroke", stylers: [{{ color: "#0F172A" }}] }},
                            {{ elementType: "labels.text.fill", stylers: [{{ color: "#E5E7EB" }}] }},
                            {{ featureType: "water", elementType: "geometry", stylers: [{{ color: "#0F172A" }}] }}
                        ]
                    }});
                }}

                eventSource.onmessage = function(e) {{
                    const data = JSON.parse(e.data);
                    updateTable(data);
                    updateMap(data);
                }};

                function updateTable(data) {{
                    let table = tableDiv.querySelector('table') || createTable();
                    const row = table.insertRow(-1);
                    
                    row.innerHTML = `
                        <td>${{data.IP}}</td>
                        <td>${{data.City}}</td>
                        <td>${{data.Country}}</td>
                        <td>${{data.Latitude}}, ${{data.Longitude}}</td>
                        <td>${{data.ISP}}</td>
                    `;
                }}

                function createTable() {{
                    const table = document.createElement('table');
                    table.innerHTML = `
                        <tr>
                            <th>IP</th>
                            <th>City</th>
                            <th>Country</th>
                            <th>Coordinates</th>
                            <th>ISP</th>
                        </tr>
                    `;
                    tableDiv.appendChild(table);
                    return table;
                }}

                function updateMap(data) {{
                    if (data.Latitude && data.Longitude) {{
                        new google.maps.Marker({{
                            position: {{lat: parseFloat(data.Latitude), lng: parseFloat(data.Longitude)}},
                            map: map,
                            title: data.IP
                        }});
                    }}
                }}
            </script>
            <script async defer
                src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
            </script>
        </body>
        </html>
        """

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def geolocation_worker(handler):
    while True:
        ip = sys.stdin.readline().strip()
        if ip:
            try:
                ipaddress.ip_address(ip)
                data = get_ip_location(ip)
                broadcast_data(handler, data)
            except ValueError:
                print(f"Invalid IP: {ip}")

def get_ip_location(ip):
    try:
        response = requests.get(f"https://web-api.nordvpn.com/v1/ips/lookup/{ip}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return {
            'IP': ip,
            'City': data.get('city', 'N/A'),
            'Country': data.get('country', 'N/A'),
            'Latitude': data.get('coordinates', {}).get('lat', 'N/A'),
            'Longitude': data.get('coordinates', {}).get('lng', 'N/A'),
            'ISP': data.get('asn', {}).get('name', 'N/A')
        }
    except Exception as e:
        return {'error': str(e)}

def broadcast_data(handler, data):
    message = f"data: {json.dumps(data)}\n\n"
    for client in handler.clients[:]:
        try:
            client.write(message.encode('utf-8'))
            client.flush()
        except:
            handler.clients.remove(client)

if __name__ == '__main__':
    server = ThreadedHTTPServer(('localhost', 8000), IPStreamHandler)
    threading.Thread(target=geolocation_worker, args=(IPStreamHandler,)).start()
    
    print("Server running at http://localhost:8000")
    print("Enter IP addresses in the console (one per line)")
    server.serve_forever()