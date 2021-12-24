import uasyncio
import picoweb
import ulogging as logging
import ujson
import re

class Webserver(picoweb.WebApp):
    def __init__(self, display_web, meowton):
        ROUTES = [
            ("/", self.index),
            ("/events", self.events),
            (re.compile("^/rpc/(.+)"), self.rpc),
            (re.compile("^/(static/.+)"), self.handle_static)
        ]
 
        logging.basicConfig(level=logging.WARNING)
        # logging.basicConfig(level=logging.DEBUG)

        self.display_web=display_web
        self.meowton=meowton
        super().__init__(__name__, ROUTES, serve_static=False)

    async def handle_exc(self, req, resp, exc):
        # Per API contract, handle_exc() must not raise exceptions
        # (unless we want the whole webapp to terminate).
        print("Webserver exception: "+repr(exc))


    def handle_static(self, req, resp):
        path = req.url_match.group(1)
        if ".." in path:
            yield from self.http_error(resp, "403")
            return
        yield from self.sendfile(resp, path, headers="Cache-Control: public, max-age=6048000, immutable\r\n")


    def index(self, req, resp):
        headers="Cache-Control: public, max-age=6048000, immutable\r\nLocation: /static/index.html"
        yield from picoweb.start_response(resp, status="301", headers=headers)


    #send events with scale updates to client
    def events(self, req, resp):
        yield from resp.awrite("HTTP/1.0 200 OK\r\n")
        yield from resp.awrite("Content-Type: text/event-stream\r\n")
        yield from resp.awrite("\r\n")
        try:
            last_v=-1
            while True:
                if self.display_web.state['v']!=last_v:
                    yield from resp.awrite("data: %s\n\n" % ujson.dumps(self.display_web.state))
                    last_v=self.display_web.state['v']
                yield from uasyncio.sleep(0.5)
        except OSError:
            # print("Event source connection closed")
            yield from resp.aclose()

    #handle rpc
    def rpc(self, req, resp):

        try:
            attributes=req.url_match.group(1).split(".")

            #read and parse post-data json
            size = int(req.headers[b"Content-Length"])
            if size:
                data = yield from req.reader.readexactly(size)
                data=ujson.loads(data)
            else:
                data={}

            #determine function
            current_attribute=self.meowton
            for attribute in attributes:
                current_attribute=getattr(current_attribute, attribute)

            #call the function one and return json
            yield from picoweb.jsonify(resp, current_attribute(**data))

        except Exception as e:
            yield from picoweb.start_response(resp, status=500)
            yield from resp.awrite(str(e))
            raise

    def server(self):
        self.debug=-1
        self.log=False
        return uasyncio.start_server(self._handle, "0.0.0.0", 80)
