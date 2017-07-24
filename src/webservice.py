#!/usr/bin/env python
'''
/***********************************************
*    Title: Songs Platform                     *
*    Author: Guillem Nicolau Alomar Sitjes     * 
*    Date: July 23rd, 2017                     *
*    Code version: 0.1                         *
*    Availability: Public                      *
***********************************************/
'''
import argparse
import web
import json
from datetime import datetime
import sqlite3
import os.path
import errno


class MyApplication(web.application):
    # This method initializes the web server on a specified hostname and port,
    # and through a web server gateway interface
    def run(self, app_hostname, app_port, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, (app_hostname, app_port))


def initialize_db(db_file_name):
    # This method checks if the file exists, and if not, tries to create the
    # folder containing it, and a blank file in that path. After that, returns
    # a SQLite database instance linked to that file. 'check_same_thread
    # parameter needs to be set to False to avoid problems between petitions.
    if not os.path.exists(os.path.dirname(db_file_name)):
        try:
            os.makedirs(os.path.dirname(db_file_name))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    if not os.path.isfile(db_file_name):
        db_file = open(db_file_name, 'w')
    else:
        db_file = open(db_file_name, 'r')
    db_file.close()
    return sqlite3.connect(db_file_name, check_same_thread=False)

# Links between urls and classes
urls = (
    '/add_channel', 'AddChannel',
    '/add_performer', 'AddPerformer',
    '/add_song', 'AddSong',
    '/add_play', 'AddPlay',
    '/get_channel_plays', 'GetChannelPlays',
    '/get_song_plays', 'GetSongPlays',
    '/get_top', 'GetTop'
)

db = initialize_db('data/dbfile.sqlite')


class AddChannel:
    # This method inserts a specified channel_name into the SQLite DB
    def POST(self):
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels(id INTEGER PRIMARY KEY, channel_name TEXT)
        ''')
        cursor.execute('''INSERT INTO channels(channel_name)
                          VALUES(?)''', (str(web.input().name),))
        db.commit()


class AddPerformer:
    # This method inserts a specified performer_name into the SQLite DB
    def POST(self):
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performers(id INTEGER PRIMARY KEY, performer_name TEXT)
        ''')
        cursor.execute('''INSERT INTO performers(performer_name)
                          VALUES(?)''', (str(web.input().name),))
        db.commit()


class AddSong:
    # This method inserts a specified song name and performer into the SQLite DB
    def POST(self):
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY, song_name TEXT, song_performer TEXT)
        ''')
        cursor.execute('''INSERT INTO songs(song_name, song_performer)
                          VALUES(?, ?)''', (web.input().title, web.input().performer))
        db.commit()


class AddPlay:
    # This method inserts a specified play into the SQLite DB
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


class GetChannelPlays:
    # This method retrieves all songs from a specified channel that were
    # reproduced during a specified period of time.
    def GET(self):
        errors = []
        try:
            curr_channel = web.input().channel
            from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
            to_time = datetime.strptime(web.input().end, '%Y-%m-%dT%H:%M:%S')
        except Exception as e:
            errors.append(str(e) + ". Not all parameters where given, or their format is incorrect.")
        result = []
        cursor = db.cursor()
        try:
            cursor.execute('''SELECT * FROM plays''')
            plays = cursor.fetchall()
        except sqlite3.OperationalError as e:
            errors.append(str(e) + ". To load test data, run the application with option '--add-data")
        if len(errors) == 0:
            for play in plays:
                if str(play[1]) == curr_channel and \
                   datetime.strptime(str(play[4]), '%Y-%m-%d %H:%M:%S') > from_time and \
                   datetime.strptime(str(play[5]), '%Y-%m-%d %H:%M:%S') < to_time:
                    result.append({'performer': play[3],
                                   'title': play[2],
                                   'start': play[4],
                                   'end': play[5]})
            return json.dumps({'result': result, 'code': 0})
        else:
            return json.dumps({'result': result, 'code': len(errors), 'errors': list(errors)})


class GetSongPlays:
    # This method retrieves all the times a song was played in any channel,
    # during a specified period of time.
    def GET(self):
        errors = []
        try:
            title = web.input().title
            from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
            to_time = datetime.strptime(web.input().end, '%Y-%m-%dT%H:%M:%S')
        except Exception as e:
            errors.append(str(e) + ". Not all parameters where given, or their format is incorrect.")
        result = []
        cursor = db.cursor()
        try:
            cursor.execute('''SELECT * FROM plays''')
            plays = cursor.fetchall()
        except sqlite3.OperationalError as e:
            errors.append(str(e) + ". To load test data, run the application with option '--add-data")
        if len(errors) == 0:
            for play in plays:
                if str(play[2]) == title and \
                   datetime.strptime(str(play[4]), '%Y-%m-%d %H:%M:%S') > from_time and \
                   datetime.strptime(str(play[5]), '%Y-%m-%d %H:%M:%S') < to_time:
                    result.append({'channel': play[1],
                                   'start': play[4],
                                   'end': play[5]})
            return json.dumps({'result': result, 'code': 0})
        else:
            return json.dumps({'result': result, 'code': len(errors), 'errors': list(errors)})


class GetTop:
    # This method returns a ranking with the most played songs since a
    # specified time, in descending order. It also returns the previous
    # rank of the song.
    def GET(self):
        errors = []
        try:
            curr_channels = json.loads(web.input().channels)
            from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
            limit = int(web.input().limit)
        except Exception as e:
            errors.append(str(e) + ". Not all parameters where given, or their format is incorrect.")
        result = []
        cursor = db.cursor()
        try:
            cursor.execute('''SELECT * FROM plays''')
            plays = cursor.fetchall()
        except sqlite3.OperationalError as e:
            errors.append(str(e) + ". To load test data, run the application with option '--add-data")
        if len(errors) == 0:
            songs_to_return = {}
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
            filtered_songs = [(k, v['plays'], v['previous_plays']) for k, v in songs_to_return.iteritems()]
            for ind, song in enumerate(sorted(filtered_songs,
                                              key=lambda tup: tup[1],
                                              reverse=True)):
                songs_to_return[song[0]]['rank'] = ind
            for ind, song in enumerate(sorted(filtered_songs,
                                              key=lambda tup: tup[2],
                                              reverse=True)):
                songs_to_return[song[0]]['previous_rank'] = ind
            for ind, song in enumerate(songs_to_return.values()):
                result.append(song)
            result = sorted(result, key=lambda k: k['plays'], reverse=True)
            return json.dumps({'result': result[0:limit], 'code': 0})
        else:
            return json.dumps({'result': result, 'code': len(errors), 'errors': list(errors)})


if __name__ == "__main__":
    # Arguments are taken from command line
    parser = argparse.ArgumentParser(description='Web Crawler')
    parser.add_argument('-H', action="store", dest="hostname",
                        default="localhost", type=str)
    parser.add_argument('-P', action="store", dest="port",
                        default=8080, type=int)
    args = parser.parse_args()

    hostname = args.hostname
    port = args.port

    # An instance of the server is created
    app = MyApplication(urls, globals())
    # and run
    app.run(hostname, port)
