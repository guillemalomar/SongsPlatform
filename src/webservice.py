#!/usr/bin/env python
import web
import json
from datetime import datetime
import sqlite3
import os.path
import io


class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('127.0.0.1', port))

urls = (
    '/add_channel', 'add_channel',
    '/add_performer', 'add_performer',
    '/add_song', 'add_song',
    '/add_play', 'add_play',
    '/get_channel_plays', 'get_channel_plays',
    '/get_song_plays', 'get_song_plays',
    '/get_top', 'get_top'
)

app = web.application(urls, globals())
if not os.path.isfile('data/dbfile.sqlite'):
    db_file = open('data/dbfile.sqlite', 'w')
else:
    db_file = open('data/dbfile.sqlite', 'r')
db = sqlite3.connect("data/dbfile.sqlite", check_same_thread=False)

class add_channel:
    def POST(self):
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels(id INTEGER PRIMARY KEY, channel_name TEXT)
        ''')
        cursor.execute('''INSERT INTO channels(channel_name)
                          VALUES(?)''', (str(web.input().name),))
        db.commit()


class add_performer:
    def POST(self):
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performers(id INTEGER PRIMARY KEY, performer_name TEXT)
        ''')
        cursor.execute('''INSERT INTO performers(performer_name)
                          VALUES(?)''', (str(web.input().name),))
        db.commit()


class add_song:
    def POST(self):
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY, song_name TEXT, song_performer TEXT)
        ''')
        cursor.execute('''INSERT INTO songs(song_name, song_performer)
                          VALUES(?, ?)''', (web.input().title, web.input().performer))
        db.commit()


class add_play:
    def POST(self):
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plays(id INTEGER PRIMARY KEY,
            channel_name TEXT, song_name TEXT, song_performer TEXT,
            start_time DATETIME, end_time DATETIME)
        ''')
        cursor.execute('''INSERT INTO plays(channel_name, song_name, song_performer, start_time, end_time)
                          VALUES(?,?,?,?,?)''', (web.input().channel, web.input().title, web.input().performer,
                                                 datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S'),
                                                 datetime.strptime(web.input().end, '%Y-%m-%dT%H:%M:%S')))
        db.commit()


class get_channel_plays:
    def GET(self):
        curr_channel = web.input().channel
        from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
        to_time = datetime.strptime(web.input().end, '%Y-%m-%dT%H:%M:%S')
        result = []
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM plays''')
        plays = cursor.fetchall()
        for play in plays:
            if str(play[1]) == curr_channel and \
               datetime.strptime(str(play[4]), '%Y-%m-%d %H:%M:%S') > from_time and \
               datetime.strptime(str(play[5]), '%Y-%m-%d %H:%M:%S') < to_time:
                result.append({'performer': play[3],
                               'title': play[2],
                               'start': play[4],
                               'end': play[5]})
        return json.dumps({'result': result, 'code': 0})


class get_song_plays:
    def GET(self):
        title = web.input().title
        from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
        to_time = datetime.strptime(web.input().end, '%Y-%m-%dT%H:%M:%S')
        result = []
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM plays''')
        plays = cursor.fetchall()
        for play in plays:
            if str(play[2]) == title and \
               datetime.strptime(str(play[4]), '%Y-%m-%d %H:%M:%S') > from_time and \
               datetime.strptime(str(play[5]), '%Y-%m-%d %H:%M:%S') < to_time:
                result.append({'channel': play[1],
                               'start': play[4],
                               'end': play[5]})
        return json.dumps({'result': result, 'code': 0})

class get_top:
    def GET(self):
        curr_channels = json.loads(web.input().channels)
        from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
        limit = web.input().limit
        result = []
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM plays''')
        plays = cursor.fetchall()
        songs_to_return = {}
        ind = 0
        for play in filter(lambda x: x[1] in curr_channels, plays):
            if play[2] not in songs_to_return.keys():
                songs_to_return[play[2]] = {str('performer'): play[3],
                                            str('title'): play[2],
                                            str('rank'): 0,
                                            str('previous_rank'): None,
                                            str('plays'): 0,
                                            str('previous_plays'): 0}
            if datetime.strptime(str(play[4]), '%Y-%m-%d %H:%M:%S') < from_time:
                songs_to_return[play[2]]['previous_plays'] += 1
            else:
                songs_to_return[play[2]]['plays'] += 1
            ind += 1
            if ind > limit:
                break
        filtered_songs = [(k, v['plays'], v['previous_plays']) for k, v in songs_to_return.iteritems()]
        for ind, song in enumerate(sorted(filtered_songs,
                                          key=lambda tup: tup[1],
                                          reverse=True)):
            songs_to_return[song[0]]['rank'] = ind
        for ind, song in enumerate(sorted(filtered_songs,
                                          key=lambda tup: tup[2],
                                          reverse=True)):
            songs_to_return[song[0]]['previous_rank'] = ind
        for song in songs_to_return.values():
            result.append(song)
        result = sorted(result, key=lambda k: k['plays'], reverse=True)
        return json.dumps({'result': result, 'code': 0})


if __name__ == "__main__":
    app = MyApplication(urls, globals())
    app.run()
