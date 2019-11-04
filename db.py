import json

def dbc():
    try:
        db = json.load(open('db.json','r'))
    except FileNotFoundError:
        with open('db.json','w') as memoria:
            memoria.write('{}')
        db = json.load(open('db.json','r'))
    return db

def save(rq):
    mem = open('db.json','w')
    json.dump(rq,mem)
    mem.close()
    return True