#!/usr/bin/env python
import web
import json
from datetime import datetime


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

channels = []
performers = []
songs = []
plays = []


class add_channel:
    def POST(self):
        channels.append(web.input().name)


class add_performer:
    def POST(self):
        performers.append(web.input().name)


class add_song:
    def POST(self):
        songs.append((web.input().title,
                      web.input().performer))


class add_play:
    def POST(self):
        plays.append((web.input().channel,
                      web.input().title,
                      web.input().performer,
                      datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S'),
                      datetime.strptime(web.input().end, '%Y-%m-%dT%H:%M:%S')))


class get_channel_plays:
    def GET(self):
        curr_channel = web.input().channel
        from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
        to_time = datetime.strptime(web.input().end, '%Y-%m-%dT%H:%M:%S')
        result = []
        for plays_info in filter(lambda x: x[0] == curr_channel, plays):
            if plays_info[3] > from_time and plays_info[4] < to_time:
                result.append({'performer': plays_info[2],
                               'title': plays_info[1],
                               'start': plays_info[3].isoformat(),
                               'end': plays_info[4].isoformat()})
        return json.dumps({'result': result, 'code': 0})


class get_song_plays:
    def GET(self):
        title = web.input().title
        from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
        to_time = datetime.strptime(web.input().end, '%Y-%m-%dT%H:%M:%S')
        result = []
        for song_info in filter(lambda x: x[1] == title, plays):
            if song_info[3] >= from_time and song_info[4] <= to_time:
                result.append({'channel': song_info[0],
                               'start': song_info[3].isoformat(),
                               'end': song_info[4].isoformat()})
        return json.dumps({'result': result, 'code': 0})

class get_top:
    def GET(self):
        curr_channels = json.loads(web.input().channels)
        print "channels:", channels
        from_time = datetime.strptime(web.input().start, '%Y-%m-%dT%H:%M:%S')
        limit = web.input().limit
        result = []
        songs_to_return = {}
        ind = 0
        for play_info in filter(lambda x: x[0] in curr_channels, plays):
            if play_info[1] not in songs_to_return.keys():
                songs_to_return[play_info[1]] = {str('performer'): play_info[2],
                                                 str('title'): play_info[1],
                                                 str('rank'): 0,
                                                 str('previous_rank'): None,
                                                 str('plays'): 0,
                                                 str('previous_plays'): 0}
            if play_info[3] < from_time:
                songs_to_return[play_info[1]]['previous_plays'] += 1
            else:
                songs_to_return[play_info[1]]['plays'] += 1
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
