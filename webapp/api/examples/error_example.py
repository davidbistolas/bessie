import json

from tornado.web import asynchronous

from apphandler.application import Loadable


class ErrorExample(Loadable):
    @asynchronous
    def get(self, *args, **kwargs):
        result = {"data": "some data"}
        an_unknown_method

        self.write(json.dumps(result))
        self.finish()
