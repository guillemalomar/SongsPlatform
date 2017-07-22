#!/usr/bin/env python
import web


class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('127.0.0.1', port))


urls = (
    '/get_channel_plays', 'get_channel_plays',
    '/add_channel', 'add_channel',
    '/add_performer', 'add_performer',
    '/add_song', 'add_song',
    '/add_play', 'add_play'
)

app = web.application(urls, globals())

channels = []
performers = []
songs = []
plays = []

class get_channel_plays:
    def GET(self):
        print "get called"


class add_channel:
    def POST(self):
        print "add_channel"
        channels.append(web.input().name)


class add_performer:
    def POST(self):
        print "add_performer"
        performers.append(web.input().name)


class add_song:
    def POST(self):
        print "add_song"
        songs.append((web.input().title,
                     web.input().performer))


class add_play:
    def POST(self):
        print "add_play"
        plays.append((web.input().title,
                     web.input().performer,
                     web.input().channel,
                     web.input().start,
                     web.input().end))

if __name__ == "__main__":
    app = MyApplication(urls, globals())
    app.run()
