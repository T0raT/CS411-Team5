import openai, requests, json, time, os, random
from flask import Flask, request, url_for, session, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import spotipy
import mysql.connector
import requests
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()


# NEVER push the actual key to GitHub, create and keep in .env file
# Create a .env if you don't have one already
app.secret_key = os.getenv("secret_key")
app.config['SESSION_COOKIE_NAME'] = os.getenv('secret_config')
openai.api_key = os.getenv("H2H_Key")
TOKEN_INFO = "token_info"




@app.route('/')
def login():
    return render_template('landingpage.html')

@app.route('/auth')
def auth():
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
        redirect(url_for("login", _external=False))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    # Get top 30 tracks for the past month
    top_tracks = sp.current_user_top_tracks(limit=30, offset=0, time_range='short_term')['items']
    # Get top 30 artists for the past month
    top_artists = sp.current_user_top_artists(limit=30, offset=0, time_range='short_term')['items']
    return render_template('top_tracks_and_artists.html', top_tracks=top_tracks, top_artists=top_artists)


@app.route('/generate_cover')
def generate_cover():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    top_tracks = sp.current_user_top_tracks(limit=5, offset=0, time_range='short_term')['items']
    song_titles = [track['name'] for track in top_tracks]
    prompt_temp = f"An album cover for a compilation of these songs: {', '.join(song_titles)}"
    print(prompt_temp)
    image_url = generate_image(prompt_temp)

    if image_url:
        return render_template('album_cover.html', image_url=image_url)
    else:
        return render_template('error.html', message="Error generating album cover")


@app.route('/generate_cover_random')
def generate_cover_random():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    top_tracks = sp.current_user_top_tracks(limit=50, offset=0, time_range='short_term')['items']
    song_titles = [track['name'] for track in top_tracks]
    song_random = random.sample(song_titles, 5)
    prompt_temp = f"An album cover for a compilation of these songs: {', '.join(song_random)}"
    print(prompt_temp)
    image_url = generate_image(prompt_temp)
    if image_url:
        return render_template('album_cover.html', image_url=image_url)
    else:
        return render_template('error.html', message="Error generating album cover")


@app.route('/generate_cover_artistGenre')
def generate_cover_artistGenre():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    top_artists = sp.current_user_top_artists(limit=5, offset=0, time_range='short_term')['items']
    top_genres = []
    for artist in top_artists:
        if artist['genres']:
            top_genres.append(', '.join(artist['genres']))

    top_genres = ', '.join(top_genres)
    print(top_genres)
    prompt_temp = f"An album cover for a compilation of these genres: {top_genres}"
    print(prompt_temp)
    image_url = generate_image(prompt_temp)
    if image_url:
        return render_template('album_cover.html', image_url=image_url)
    else:
        return render_template('error.html', message="Error generating album cover")


def generate_image(prompt_temp):
    response = openai.Image.create(
        prompt= prompt_temp,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    return image_url


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
        redirect_uri=url_for('redirectSite', _external=True),
        scope="user-top-read, user-library-read"
    )

@app.route('/songstorage')
def dbconnector():
    # connecting to the MySQL Database
    db = mysql.connector.connect(
        user = 'root',
        password = 'root',
        host = 'localhost',
        database = 'H2HDB'
    )
    
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"

    token_info = get_token()['access_token']
    
    headers = {
        "Authorization": f"Bearer {token_info}"
    }
    
    params = {
        "limit": 30,
        "time_range": "short_term"
    }

    cursor = db.cursor()

    table = "CREATE TABLE IF NOT EXISTS top_songs(track_name VARCHAR(100), artist_name VARCHAR(100), track_popularity VARCHAR(3));"
    cursor.execute(table)
    insert_st = "INSERT INTO top_songs VALUES(%s, %s, %s);"

    response = requests.get(top_tracks_url, headers=headers, params=params)
    top_tracks_data = response.json()["items"]

    for track in top_tracks_data:
        track_name = track["name"]
        print("track name: ", track_name)
        artist_name = track["artists"][0]["name"]
        print("artist name: ", artist_name)
        track_popularity = track["popularity"]
        print("track popularity: ", track_popularity)
        values = (track_name, artist_name, track_popularity)
        print()
        cursor.execute(insert_st, values)
    
    top_artists_url = "https://api.spotify.com/v1/me/top/artists"

    headers2 = {
        "Authorization": f"Bearer {token_info}"
    }
    
    params2 = {
        "limit": 30,
        "time_range": "short_term"
    }

    table2 = "CREATE TABLE IF NOT EXISTS top_artists(artist_name VARCHAR(100), plays VARCHAR(200));"
    cursor.execute(table2)
    insert2_st = "INSERT INTO top_artists VALUES(%s, %s);"

    response2 = requests.get(top_artists_url, headers=headers2, params=params2)
    top_artists_data = response2.json()["items"]

    for artist in top_artists_data:
        artist_name = artist["name"]
        plays = artist["popularity"]
        values = (artist_name, plays)
        cursor.execute(insert2_st, values)

    db.commit()
    db.close()

    return {'message': 'Tracks exported successfully'}