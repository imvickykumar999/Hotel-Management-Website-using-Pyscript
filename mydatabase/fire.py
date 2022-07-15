
from firebase_admin import credentials

cred = credentials.Certificate('mydatabase/cred.json')
# cred = credentials.Certificate('cred.json')

url = 'https://neosalpha-999-default-rtdb.firebaseio.com/'
path = {'databaseURL' : url}

import firebase_admin
# https://stackoverflow.com/a/44501290/11493297

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, path)

from firebase_admin import db


def call():
    refv = db.reference('Hotel/Database/Rooms')
    name = refv.get()
    return name


# -----------------( SAMPLE DATA ENTRY )----------------------------

# def sample_room():
#     import random

#     for i in range(1, 21):
#         status = ['booked', 'empty']
#         ran = random.randint(1,2)

#         data = status[ran%2]
#         refv = db.reference(f'Hotel/Database/Rooms/room_{i}')
#         refv.set(data)


# def sample_customer():
#     import random

#     for _ in range(1, 11):
#         ran = random.randint(1,11)
#         cid = random.randint(1000,9999)

#         data = {'booked': ran}
#         refv = db.reference(f'Hotel/Database/Customer/{cid}')
#         refv.set(data)


# sample_customer()
# sample_room()

# refv = db.reference('Hotel/Database')
# name = refv.get()
# print(name)
