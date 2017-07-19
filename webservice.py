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


class get_channel_plays:
    def GET(self):
        print "get called"


class add_channel:
    def POST(self):
        print "name"


class add_performer:
    def POST(self):
        print "name"


class add_song:
    def POST(self):
        print "name"


class add_play:
    def POST(self):
        print "name"

if __name__ == "__main__":
    app = MyApplication(urls, globals())
    app.run()
