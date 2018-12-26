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
                req_data = 'measurements,cat={},scale={} weight={},food={},feed_daily={}'.format(cat.state.name, config.id, cat.state.weight, cat.ate_session, cat.state.feed_daily)
                resp=urequests.post(config.db, data=req_data, headers={ 'Content-Type': 'text/plain' })

                print('HTTP response "{}", text: {} '.format(resp.reason,resp.text))

                if resp.status_code!=204:
                    self.display.msg("Database error.")
                else:
                    self.display.msg("")
                    return True

            except Exception as e:
                print('HTTP error: {}'.format(e))
                self.display.msg("Network error.", timeout=None)
                return False
