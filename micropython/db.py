import urequests
import config

class Db():
        def __init__(self, display):
            self.display=display


        def store(self, cat):
            '''store cat statistics in db'''

             # POST data to influxdb
            try:
                self.display.msg("Uploading...")
                print("HTTP posting to {}".format(config.db))
                resp_data = 'measurements,cat={},scale={} weight={},food={}'.format(cat.state.name, config.id, cat.state.weight, cat.ate_session)
                resp = urequests.post(config.db, data=resp_data)
                print('HTTP response: {}'.format(resp))
                self.display.msg("")
            except Exception as e:
                print('HTTP error: {}'.format(e))
                self.display.msg("Upload error.", timeout=None)
