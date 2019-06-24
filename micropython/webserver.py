import uasyncio
import picoweb
import ulogging as logging
import ujson


class Webserver():
    def __init__(self, display_web):
        ROUTES = [
            ("/events", self.events),
        ]

        # logging.basicConfig(level=logging.INFO)
        logging.basicConfig(level=logging.DEBUG)

        self.display_web=display_web
        self.webapp = picoweb.WebApp(__name__, ROUTES)

    def events(self, req, resp):
        # print("Event source connected")
        yield from resp.awrite("HTTP/1.0 200 OK\r\n")
        yield from resp.awrite("Content-Type: text/event-stream\r\n")
        yield from resp.awrite("\r\n")
        try:
            last_v=-1
            while True:
                if self.display_web.state['v']!=last_v:
                    yield from resp.awrite("data: %s\n\n" % ujson.dumps(self.display_web.state))
                    last_v=self.display_web.state['v']
                yield from uasyncio.sleep(0.25)
        except OSError:
            # print("Event source connection closed")
            yield from resp.aclose()

    def run(self):
        self.webapp.run(debug=-1, host="0.0.0.0", port=80)
