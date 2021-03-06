import uasyncio
import picoweb
import ulogging as logging
import ujson
import meowton
import re


class ExcWebApp(picoweb.WebApp):

    async def handle_exc(self, req, resp, exc):
        # Per API contract, handle_exc() must not raise exceptions
        # (unless we want the whole webapp to terminate).
        print("Webserver exception: "+repr(exc))


class Webserver():
    def __init__(self, display_web):
        ROUTES = [
            ("/", self.index),
            ("/events", self.events),
            (re.compile("^/rpc/(.+)"), self.rpc),
            (re.compile("^/(static/.+)"), self.handle_static)
        ]
 
        logging.basicConfig(level=logging.WARNING)
        # logging.basicConfig(level=logging.DEBUG)

        self.display_web=display_web
        self.webapp = ExcWebApp(__name__, ROUTES, serve_static=False)

    def handle_static(self, req, resp):
        path = req.url_match.group(1)
        if ".." in path:
            yield from self.webapp.http_error(resp, "403")
            return
        yield from self.webapp.sendfile(resp, path, headers="Cache-Control: public, max-age=6048000, immutable\r\n")


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
            current_attribute=meowton
            for attribute in attributes:
                current_attribute=getattr(current_attribute, attribute)

            #call the function one and return json
            yield from picoweb.jsonify(resp, current_attribute(**data))

        except Exception as e:
            yield from picoweb.start_response(resp, status=500)
            yield from resp.awrite(str(e))
            raise



    def run(self):
        self.webapp.run(debug=0, host="0.0.0.0", port=80)
