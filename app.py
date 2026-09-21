import os
import binascii
import requests
from flask import Flask, request, send_file

def generate_secret_key():
    secret_key = os.urandom(32)
    return binascii.hexlify(secret_key).decode('utf-8')

app = Flask(__name__)
app.secret_key = generate_secret_key()

IP_GEOLOCATION_API = 'http://api.ipapi.com/'
API_KEY = os.environ.get('IPAPI_KEY', '')


def log_visitor(user_ip: str) -> None:
    if not API_KEY:
        return
    try:
        response = requests.get(
            f'{IP_GEOLOCATION_API}/{user_ip}?access_key={API_KEY}',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            country = data.get('country_name', 'Unknown')
            city = data.get('city', 'Unknown')
            with open("info.txt", 'a') as f:
                f.write(f"New IP visited: {user_ip}\n{user_ip}'s Country: {country}\n{user_ip}'s City: {city}\n\n")
    except requests.RequestException:
        pass


@app.route("/<string:image_name>")
def site(image_name: str):
    if not image_name.endswith(".png") or not os.path.exists(image_name):
        return "Please enter a valid image.", 404
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    log_visitor(user_ip)
    return send_file(image_name, mimetype="image/png")


@app.route("/")
def index():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    log_visitor(user_ip)
    return send_file("image.png", mimetype="image/png")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
