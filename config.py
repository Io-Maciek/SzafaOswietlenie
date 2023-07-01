import json
import os.path


_file = os.path.abspath(__file__)
_parent = os.path.dirname(_file)
_config_path = os.path.join(_parent, 'config.json')


class Config:
    def __init__(self, override=False, alarm=2, godzina_start=0, godzina_end=0):
        self.override = override
        self.alarm = alarm
        self.godzina_start = godzina_start
        self.godzina_end = godzina_end

    @staticmethod
    def read():
        if os.path.isfile(_config_path):
            with open(_config_path, 'r') as f:
                file_text = f.read()
            d = json.loads(file_text)
            return Config(d['override'], d['alarm'], d['g_start'], d['g_end'])
        else:
            return Config()

    def write(self):
        d = {'override': self.override, 'alarm': self.alarm, 'g_start': self.godzina_start, 'g_end': self.godzina_end}
        with open(_config_path, 'w') as f:
            f.write(json.dumps(d))

    def __str__(self):
        return 'Config:\n\toverride: {}\n\talarm: {}\n\tstart: {}\n\tend: {}'\
            .format(self.override, self.alarm, self.godzina_start, self.godzina_end)
