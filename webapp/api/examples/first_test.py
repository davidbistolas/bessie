from tornado.web import asynchronous
from apphandler.application import Loadable


class Application(Loadable):

    @asynchronous
    def get(self, *args, **kwargs):
        self.write("Here we go!")
        self.finish()

