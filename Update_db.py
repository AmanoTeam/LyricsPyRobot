import json
import db as d

db = json.load(open('db.json', 'r'))

for i in db:
    d.add_user(int(i), db[i]['access_token'], db[i]['refresh_token'])