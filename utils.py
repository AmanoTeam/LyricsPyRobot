import spotipy
from spotipy.client import SpotifyException
import requests
import db
from config import BASIC, KEY

def get_token(user_id, auth_code):
    b = requests.post("https://accounts.spotify.com/api/token",
                      headers=dict(
                          Authorization=f"Basic {BASIC}"
                      ),
                      data=dict(
                          grant_type="authorization_code",
                          code=auth_code,
                          redirect_uri="https://lyricspy.ml/go"
                      )).json()
    if b.get("error"):
        return False, b['error']
    else:
        print(b)
        db.add_user(user_id, b['refresh_token'], b['access_token'])
        return True, b['access_token']

def refresh_token(user_id):
    print('refreh')
    tk = db.get(user_id)
    print(tk[1])
    b = requests.post("https://accounts.spotify.com/api/token",
                      headers=dict(
                          Authorization=f"Basic {BASIC}"
                      ),
                      data=dict(
                          grant_type="refresh_token",
                          refresh_token=tk[1]
                      )).json()
    print(b)
    db.update_user(user_id,b['access_token'])
    return b['access_token']

def get_current_playing(user_id):
    tk = db.get(user_id)
    a = spotipy.Spotify(auth=tk[0])
    try:
        return a.current_user_playing_track()
    except SpotifyException:
        new_token = refresh_token(user_id)
        a = spotipy.Spotify(auth=new_token)
        return a.current_user_playing_track()

def get_current(user):
    r = requests.get('http://ws.audioscrobbler.com/2.0/',params=dict(
        method='user.getrecenttracks',
        user=user,
        api_key=KEY,
        format='json',
        limit=1))
    return r.json()['recenttracks']['track']
