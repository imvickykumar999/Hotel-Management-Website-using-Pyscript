
from firebase_admin import credentials

cred = credentials.Certificate('mydatabase/cred.json')
url = 'https://neosalpha-999-default-rtdb.firebaseio.com/'
path = {'databaseURL' : url}

import firebase_admin
# https://stackoverflow.com/a/44501290/11493297

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, path)

from firebase_admin import db


def call(_path):
    refv = db.reference(_path)
    name = refv.get()
    return name


def sets(_path, jsondict):
    refv = db.reference(_path)
    refv.set(jsondict)


# -----------------( SAMPLE DATA ENTRY )----------------------------

# def sample_room():
#     import random

#     for i in range(1, 21):
#         refv = db.reference(f'Hotel/Database/Rooms/room_{i}')
#         refv.set('empty')

# sample_room()
# refv = db.reference('Hotel/Database')
# name = refv.get()
# print(name)
