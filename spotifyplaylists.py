import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials
import re
import sqlite3

conn = sqlite3.connect('spotifylikes.sqlite')
cur = conn.cursor()

#cid = ''
#secret = ''

cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;
DROP TABLE IF EXISTS Type;

CREATE TABLE Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Type (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id  INTEGER,
    title   TEXT UNIQUE
);

CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    album_id  INTEGER,
    type_id  INTEGER,
    duration INTEGER, popularity INTEGER, explicit INTEGER
);
''')
#spotipy authentication

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#open the likesongs url list
fname = input("Enter Spotify File Name:")
track_object= open(fname)
#print(track_object.read())
track_list = list()


#extract all the
for line in track_object:
    line=line.rstrip().split('/')[-1]
    track_list.append(line)
    #print(track_list)

#print(track_list)
#print(track_list[0].split('/')[-1])

#convert milliseconds to a  hrs,mins,seconds
def Convert_ms(millis):
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24
    return(str(minutes)+':'+str(seconds))

for song in track_list:
    print('track id:',song)
#extract the track data
    result = sp.track(song)
#print(result.keys())

#for k in result.keys():
    #print('\n'+k+':',result[k])

    track = result['name']
    artist = result['artists'][0]['name']
    album =result['album']['name']
    duration = result['duration_ms']
    popularity = result['popularity']
    explicit = result['explicit']
    if explicit: explicit =1
    else: explicit =0
    type = result['type']

    if track is None or artist is None or album is None or type is None:
        continue

    print(track, artist, album, duration, popularity, explicit, type)

    cur.execute('''INSERT OR IGNORE INTO Artist (name)
        VALUES ( ? )''', ( artist, ) )
    cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist, ))
    artist_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Type (name)
        VALUES ( ? )''', ( type, ) )
    cur.execute('SELECT id FROM Type WHERE name = ? ', (type, ))
    type_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id)
        VALUES ( ?, ? )''', ( album, artist_id ) )
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, type_id, duration, popularity, explicit)
        VALUES ( ?, ?, ?, ?, ?, ? )''',
        ( track, album_id, type_id, duration, popularity, explicit ) )

    conn.commit()
