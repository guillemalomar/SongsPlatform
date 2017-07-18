#!/usr/bin/env python
import web


urls = (
    '/users', 'list_users',
    '/users/(.*)', 'get_user'
)

app = web.application(urls, globals())

class get_channel_plays:
    def GET(self):
        print "get called"

class list_users:
    def GET(self):
        pass

class get_user:
    def GET(self, user):
        pass

if __name__ == "__main__":
    app.run()