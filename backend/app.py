from flask import Flask, redirect, jsonify, send_from_directory, session
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os

static_path = os.getenv('STATIC_PATH','static')
template_path = os.getenv('TEMPLATE_PATH','templates')

app = Flask(__name__, static_folder=static_path, template_folder=template_path)
app.secret_key = os.urandom(24)

oauth = OAuth(app)
nonce = generate_token()

oauth.register(
    name=os.getenv('OIDC_CLIENT_NAME'),
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    #server_metadata_url='http://dex:5556/.well-known/openid-configuration',
    authorization_endpoint="http://localhost:5556/auth",
    token_endpoint="http://dex:5556/token",
    jwks_uri="http://dex:5556/keys",
    userinfo_endpoint="http://dex:5556/userinfo",
    device_authorization_endpoint="http://dex:5556/device/code",
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

@app.route('/')
@app.route('/<path:path>')
def home(path=''):
    user = session.get('user')
    if not user:
        return redirect('/login')
    if path != '' and os.path.exists(os.path.join(static_path,path)):
        return send_from_directory(static_path, path)
    return send_from_directory(template_path, 'index.html')

@app.route('/login')
def login():
    session['nonce'] = nonce
    redirect_uri = 'http://localhost:8000/authorize'
    client = oauth.create_client(os.getenv('OIDC_CLIENT_NAME'))
    return client.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    client = oauth.create_client(os.getenv('OIDC_CLIENT_NAME'))

    token = client.authorize_access_token()
    nonce = session.get('nonce')

    user_info = client.parse_id_token(token, nonce=nonce)  # or use .get('userinfo').json()
    session['user'] = user_info
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
