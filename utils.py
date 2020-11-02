import spotipy
from spotipy.client import SpotifyException
import requests
import db
from config import BASIC, KEY
from PIL import Image, ImageDraw, ImageFont
import textwrap
import math
import urllib.request
import os

def send(res, name, color):
    if color and color == 'black':
        color1 = 'white'
        color2 = 'black'
    else:
        color1 = 'black'
        color2 = 'white'
    wrapper = textwrap.TextWrapper(width=25)
    til = Image.new("RGB", (1280,720), color2)
    urllib.request.urlretrieve(res['item']['album']['images'][0]['url'], "00000001.jpg")

    image = Image.open("00000001.jpg")
    num = 450
    maxsize = (num, num)
    if (image.width and image.height) < num:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = num / size1
            size1new = num
            size2new = size2 * scale
        else:
            scale = num / size2
            size1new = size1 * scale
            size2new = num
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    til.paste(image,(48,135))
    os.remove("00000001.jpg")
    b = ImageDraw.Draw(til)
    font = ImageFont.truetype("Oblik_Bold.otf",1)
    waped = wrapper.wrap(text=res['item']['name'])
    text = '\n'.join(waped)
    fontsize = 1
    while font.getsize(waped[0])[0] < 1.5*image.size[0]:
        fontsize += 5
        font = ImageFont.truetype("Oblik_Bold.otf", fontsize)
    b.text((550,145), text, color1, font=font)

    font = ImageFont.truetype("Oblik_Bold.otf", 51)
    b.text((550,387), res['item']['artists'][0]['name'], color1, font=font)

    duration = res['item']['duration_ms']
    progress = res['progress_ms']
    print(progress)

    s1=int((duration/1000)%60)
    if len(str(s1))==1:
        s1=f'0{s1}'

    s2=int((progress/1000)%60)
    if len(str(s2))==1:
        s2=f'0{s2}'
    dur = f'{int((duration/(1000*60))%60)}:{s1}'
    pog = f'{int((progress/(1000*60))%60)}:{s2}'

    font = ImageFont.truetype("Oblik_Bold.otf", 27)
    b.text((547,516), pog, color1, font=font)
    b.text((1170,516), dur, color1, font=font)
    
    x, y, w, h, m = 541,470,643,43,5

    b.rectangle((x+w,y,x+h+w,y+h),fill=color1)
    b.rectangle((x,y,x+h,y+h),fill=color1)
    b.rectangle((x+(h/2),y, x+w+(h/2), y+h),fill=color1)
    b.rectangle((x+w+m,y+m,x+h+w-m,y+h-m),fill=color2)
    b.rectangle((x+m,y+m,x+h-m,y+h-m),fill=color2)
    b.rectangle((x+(h/2)+m,y+m, x+w+(h/2)-m, y+h-m),fill=color2)

    temp = progress/duration

    if(temp<=0):
        temp = 0.00001
    if(temp>1):
        temp = 1
    
    w = w*temp

    b.rectangle((x+w,y,x+h+w,y+h),fill=color1)
    b.rectangle((x,y,x+h,y+h),fill=color1)
    b.rectangle((x+(h/2),y, x+w+(h/2), y+h),fill=color1)

    til.save(f"{name}.webp")
    return f"{name}.webp"

def get_token(user_id, auth_code):
    b = requests.post("https://accounts.spotify.com/api/token",
                      headers=dict(
                          Authorization=f"Basic {BASIC}"
                      ),
                      data=dict(
                          grant_type="authorization_code",
                          code=auth_code,
                          redirect_uri="https://lyricspy.amanoteam.com/go"
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
