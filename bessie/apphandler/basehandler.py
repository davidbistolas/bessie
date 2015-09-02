import hmac
import hashlib
import base64
import time
import logging
import functools

import tornado
from tornado import web, ioloop, options
from tornado.httpclient import AsyncHTTPClient


class BaseHandler(tornado.web.RequestHandler):
    """Base request handler- all other handlers will subclass this

    Provides user authentication, admin authentication, non-blocking
    http client, hmac etc.

    All of our handlers subclass this.

    """

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.http_client = AsyncHTTPClient(
            io_loop=self.ioloop, force_instance=True, max_clients=20)
        self.logging = logging.getLogger(self.__class__.__name__)
        self.options = tornado.options.options

    def check_access(self, password, username, domain):
        """
        checks the username and password passed and authenticate
        them as necessary. Binds to ldap for this (actually, AD)
        :param password:
        :param username:
        :param domain:
        :return: bool
        """
        return True

    def get_current_user(self):
        """
        Returns the current username from the secure cookie
        :return:
        """
        return self.get_secure_cookie("username")

    def get_secure_cookie(self, name):
        """ Get the nginx compatible secure cookie"""

        cookie_secret = self.application.settings["cookie_secret"]

        encoded_cookie = self.get_cookie(name)
        if encoded_cookie is None:
            return None
        value, timestamp, cookie_hash = encoded_cookie.split("|")

        decoded_value = base64.b64decode(value)
        webapp_hash = self.hmac_for_nginx(cookie_secret, decoded_value)

        if webapp_hash != cookie_hash:
            logging.warning("Cookie hash mismatch: " + decoded_value)
            return None

        if int(timestamp) < time.time() - 2678400:
            logging.warning("Expired cookie: " + decoded_value)
            return None
        if int(timestamp) > time.time() + 2678400:
            logging.warning("Cookie from the future: " + decoded_value)
            return None
        return decoded_value

    @staticmethod
    def hmac_for_nginx(secret, data):
        """does the hmac stuff in an nginx compatible way
        :rtype : str
        :param secret:
        :param data:
        """
        return base64.b64encode(
            hmac.new(secret, data, digestmod=hashlib.sha1).digest())

    def set_secure_cookie(self, name, value, **kwargs):
        """
        Sets the nginx compatible secure cookie
        """
        cookie_secret = self.application.settings["cookie_secret"]
        timestamp = str(int(time.time()))
        webapp_hash = self.hmac_for_nginx(cookie_secret, value)
        encoded_value = base64.b64encode(value)
        cookie = encoded_value + "|" + timestamp + "|" + webapp_hash
        self.set_cookie(name, cookie)

    def set_current_user(self, username=None):
        """
        Sets the current user cookie - or clears the cookie if
        user is set to None.
        :param username:
        """
        if username:
            self.set_secure_cookie("username", username)
        else:
            self.clear_cookie("username")

    def initialize(self):
        """common init functions"""

    def fetch(
            self,
            url,
            client_key=None,
            client_cert=None,
            ca_certs=None,
            proxy_host=None,
            proxy_port=None,
            auth_username=None,
            auth_password=None,
            headers=None,
            method="GET",
            body=None,
            callback=None,
            checked=True
    ):
        """
        @params:
        see tornadowweb.asynchttpclient
        #############################################
        ## fetch encapsulates http_client.fetch.
        ## this allows the test suite to replace the
        ## fetch call with a benign function to
        ## control and test the response handling of
        ## a given function.
        #############################################

        """

        if checked:
            checked_callback = functools.partial(
                self.check_fetch_results, callback)
        else:
            checked_callback = callback

        logging.info("Loading " + url)
        self.http_client.fetch(url,
                               proxy_host=proxy_host,
                               proxy_port=proxy_port,
                               client_key=client_key,
                               client_cert=client_cert,
                               ca_certs=ca_certs,
                               auth_username=auth_username,
                               auth_password=auth_password,
                               headers=headers,
                               method=method,
                               body=body,
                               callback=checked_callback,
                               allow_nonstandard_methods=True)

    def check_fetch_results(self, callback, response):
        """
        Tornado async httpclient's error checking is raw- this hook
        will take care of it and move us on to the next callback
        step"""

        if response.code >= 200:
            if response.code < 300:
                callback(response)
            else:
                url = response.request.url
                body = str(response.request.body)
                headers = str(response.request.headers)
                code = str(response.code)
                method = str(response.request.method)
                response_body = str(response.body)
                response_headers = str(response.headers)

                error = "{} ({}) from {}\n" \
                        "  method: {}\n" \
                        " body: {}\n" \
                        " headers: {}\n" \
                        "   response_body: {}\n" \
                        " response_headers: {}".format(str(code),
                                                       method,
                                                       url,
                                                       body,
                                                       headers,
                                                       response,
                                                       response_body,
                                                       response_headers)

                logging.error(error)

                callback(response)

    def data_received(self, chunk):
        pass


class AppHandler(BaseHandler):
    """Handler for applications"""

    def __init__(self, application, request, path=None, **kwargs):
        super(AppHandler, self).__init__(application, request, **kwargs)
        self.path = path

    def initialize(self, path=None):
        """Initialize the application Handler"""
        super(AppHandler, self).initialize()

    def get(self, args):
        """Get Handler"""
        uri = "{}/{}".format(self.path, self.request.uri)
        self.write(str(uri))
        self.finish()

    def data_received(self, chunk):
        pass
