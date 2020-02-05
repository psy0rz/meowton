import uasyncio
import picoweb
import ulogging as logging
import ujson
import meowton
import re

class Webserver():
    def __init__(self, display_web):
        ROUTES = [
            ("/events", self.events),
            (re.compile("^/rpc/(.+)"), self.rpc),
        ]

        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.DEBUG)

        self.display_web=display_web
        self.webapp = picoweb.WebApp(__name__, ROUTES)

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

            current_attribute=meowton
            for attribute in attributes:
                current_attribute=getattr(current_attribute, attribute)

            #call the last one and return json
            yield from picoweb.jsonify(resp, current_attribute())

        except Exception as e:
            yield from picoweb.start_response(resp, status=500)
            yield from resp.awrite(str(e))



    def run(self):
        self.webapp.run(debug=0, host="0.0.0.0", port=80)
