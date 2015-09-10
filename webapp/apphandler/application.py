from tornado.web import asynchronous
from tornado.web import HTTPError
from apphandler.basehandler import BaseHandler

class loadable(object):

    def __init__(self, handler):
        self.handler = handler
        self.fetch = handler.fetch
        self.write = handler.write
        self.finish = handler.finish
        self.write_error = handler.write_error

    @asynchronous
    def get(self, *args, **kwargs):
        """Handle a get request"""
        raise HTTPError(status_code=404, log_message="Not Found")

    @asynchronous
    def post(self, *args, **kwargs):
        """Handle a get request"""
        raise HTTPError(status_code=404, log_message="Not Found")

    @asynchronous
    def put(self, *args, **kwargs):
        """Handle a get request"""
        raise HTTPError(status_code=404, log_message="Not Found")

    @asynchronous
    def delete(self, *args, **kwargs):
        """Handle a get request"""
        raise HTTPError(status_code=404, log_message="Not Found")

    def _stack_context_handle_exception(self, a, b, c):
        """Handle exceptions"""
        #TODO: Actually handle exceptions.
        print a,b,c
