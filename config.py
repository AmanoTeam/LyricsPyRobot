import amanobot

keys = {
        'token':'',#key of telegram-api
        'basic':'',#encrypt 'client_id:client_secret' in base64
        'client_id':'',#get in https://developer.spotify.com/
        'client_secret':''#https://developer.spotify.com/
        }

bot = amanobot.Bot(keys['token'])