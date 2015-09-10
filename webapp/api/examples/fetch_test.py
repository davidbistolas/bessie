from tornado.web import asynchronous

from apphandler.application import Loadable


class FetchTest(Loadable):
    @asynchronous
    def get(self, *args, **kwargs):
        self.fetch("http://www.google.ca", callback=self.got)

    @asynchronous
    def got(self, data):
        self.handler.write(data.body)
        self.handler.finish()
