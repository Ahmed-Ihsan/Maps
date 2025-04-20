from fastapi import FastAPI, WebSocket
import requests
import json

app = FastAPI()

def get_ip_location(ip):
    """جلب بيانات الموقع الجغرافي من API"""
    try:
        response = requests.get(f"https://web-api.nordvpn.com/v1/ips/lookup/{ip}", timeout=10)
        data = response.json()
        if response.status_code != 200:
            return None
        return {
            "ip": ip,
            "city": data.get("city", "N/A"),
            "country": data.get("country_name", "N/A"),
            "latitude": data.get("latitude", 0),
            "longitude": data.get("longitude", 0),
            "isp": data.get("org", "N/A"),
            "timezone": data.get("timezone", "N/A")
        }
    except requests.exceptions.RequestException:
        return None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        ip = await websocket.receive_text()  # استقبال IP من العميل
        location_data = get_ip_location(ip)
        if location_data:
            await websocket.send_text(json.dumps(location_data))  # إرسال البيانات كـ JSON
