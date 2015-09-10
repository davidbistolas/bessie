from tornado.web import asynchronous
from apphandler.application import loadable


class Application(loadable):

    @asynchronous
    def get(self, *args, **kwargs):
        self.write("Here we go!")
        self.finish()

