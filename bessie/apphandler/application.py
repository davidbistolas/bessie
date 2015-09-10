from tornado.web import asynchronous
from apphandler.basehandler import BaseHandler

class loadable(object):

    def __init__(self, handler):
        self.handler = handler
        self.fetch = handler.fetch

    @asynchronous
    def get(self, *args, **kwargs):
        """Handle a get request"""
        pass

    @asynchronous
    def post(self, *args, **kwargs):
        """Handle a get request"""
        pass

    @asynchronous
    def put(self, *args, **kwargs):
        """Handle a get request"""
        pass

    @asynchronous
    def delete(self, *args, **kwargs):
        """Handle a get request"""
        pass


    def _stack_context_handle_exception(self, a, b, c):
        pass