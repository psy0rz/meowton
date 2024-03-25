class ScaleSensorState:
    """used during calibration"""

    MOVING_AVG_FACTOR=0.1

    def __init__(self, value):
        self.min = value
        self.max = value
        self.start_avg = 0
        self.noise = 0
        self.moving_avg = value


    def measure(self, value):

        self.moving_avg = self.moving_avg * ( 1-self.MOVING_AVG_FACTOR) * (value*self.MOVING_AVG_FACTOR)

        if value < self.min:
            self.min=value

        if value > self.max:
            self.max=value


        ### Step 1: determining noise range and start average:
        if self.cal_states[0]['start_avg'] == None:
            # wait until we have enough measurements:
            cal_count_needed = 50
            self.msg("Measuring noise ({}%)".format(int(self.cal_count * 100 / cal_count_needed)))
            if self.cal_count == cal_count_needed:
                # done, store start_average and noise, continue to next step
                for cal_state in self.cal_states:
                    cal_state['start_avg'] = cal_state['avg']
                    cal_state['noise'] = abs(cal_state['max'] - cal_state['min']) * 2  # add huge margin
                self.cal_count = 0

        else:
            ### Step 2: detect calibration weights:
            cal_count_needed = 30

            # restart averaging when there is a big change on a sensor
            for i in range(0, self.sensor_count):
                if abs(self.cal_states[i]['avg'] - sensors[i]) > self.cal_states[i]['noise']:
                    self.cal_count = 0
                    self.cal_states[i]['avg'] = sensors[i]  # start averaging from here on
                    # self.msg("sensor {}, noise {}, avg {}, current {}".format(i, self.cal_states[i]['noise'], self.cal_states[i]['avg'], sensors[i]))

            # i=0
            # self.msg("sensor {}, noise {}, avg {}, current {}".format(i, self.cal_states[i]['noise'], self.cal_states[i]['avg'], sensors[i]))

            # there is something on a sensor?
            for i in range(0, self.sensor_count):
                if abs(self.cal_states[i]['start_avg'] - sensors[i]) > self.cal_states[i]['noise']:
                    # calibrating..
                    if self.cal_count < cal_count_needed:
                        self.msg(
                            "Calibrating sensor {} ({}%)".format(i, int(self.cal_count * 100 / cal_count_needed)))
                    # done...
                    if self.cal_count == cal_count_needed:
                        # this sensor is done now:
                        diff = self.cal_states[i]['avg'] - self.cal_states[i]['start_avg']
                        self.calibration.__factors[i] = self.calibrate_weight / diff
                    # please remove..
                    if self.cal_count > cal_count_needed:
                        self.msg("Remove weight from sensor {}".format(i))

                    return True

            # there is nothing on a sensor?
            self.msg("Place {}g on next sensor.".format(self.calibrate_weight))

            if not None in self.calibration.__factors:
                self.calibration.calibrating = False
                self.cal_states = None
                self.tarre()
                self.msg("Calbration done")
                print(self.calibration.__factors)
