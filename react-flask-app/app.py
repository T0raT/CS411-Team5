from flask import Flask, request, url_for, session, redirect, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import time
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# NEVER push the actual key to GitHub, create and keep in .env file
# Create a .env if you don't have one already
# I also have no idea what this session cookie stuff actually do[Tiger]
app.secret_key = os.getenv("secret_key")
app.config['SESSION_COOKIE_NAME'] = os.getenv('secret_config')
TOKEN_INFO = "token_info"


@app.route('/')
def login():
    return jsonify({"message": "Welcome to Head2Head"})

@app.route('/auth')
def auth():

    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})

@app.route('/redirect')
def redirectSite():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return jsonify({"access_token": token_info['access_token'], "refresh_token": token_info['refresh_token'], "expires_at": token_info['expires_at']})



@app.route('/api/getTracks')
def getTracks():
    access_token = request.headers.get('Authorization').split(" ")[1]
    sp = spotipy.Spotify(auth=access_token)
    top_tracks = sp.current_user_top_tracks(limit=30, offset=0, time_range='short_term')['items']
    top_artists = sp.current_user_top_artists(limit=30, offset=0, time_range='short_term')['items']
    return jsonify({"top_tracks": top_tracks, "top_artists": top_artists})


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


# Id and secret in .env file, create one if you dont have one
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("client_id"),
        client_secret=os.getenv("client_secret"),
        redirect_uri="http://localhost:3000/redirect",
        scope="user-top-read"
    )
    
if __name__ == '__main__':
    app.run(debug=True)