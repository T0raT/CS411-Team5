from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import time
import os
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()

#nNEVER push the actual key to github, create and keep in .env file
#Create a .env if you dont have one already
#I also have no idea what this session cookie stuff actually do[Tiger]
app.secret_key = os.getenv("secret_key")
app.config['SESSION_COOKIE_NAME'] = os.getenv('secret_config')
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectSite():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', external=True))

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        redirect(url_for("login",_external=False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return str(sp.current_user_top_tracks(limit=50, offset=0)['items'][0])

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

#Id and secret in .env file, create one if you dont have one
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id= os.getenv("client_id"),
        client_secret=os.getenv("client_secret"),
        redirect_uri=url_for('redirectSite', _external=True),
        scope="user-top-read" 
        #Scope for top tracks, unsure how to use multiple scopes [Tiger]
    )