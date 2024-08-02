import json
import os.path
from ioDeSer.ioDeSeriable import IoDeSerable
from ioDeSer import ioFile

_file = os.path.abspath(__file__)
_parent = os.path.dirname(_file)
_config_path = os.path.join(_parent, 'config.io')


class Config(IoDeSerable):
    @staticmethod
    def __io__() -> dict:
        return {"override": bool, "alarm": int, "godzina_start": int, "godzina_end": int}

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
            return ioFile.read_from_str(file_text, Config)
        else:
            return Config()

    def write(self):
        # d = {'override': self.override, 'alarm': self.alarm, 'g_start': self.godzina_start, 'g_end': self.godzina_end}
        with open(_config_path, 'w') as f:
            ioFile.write_to_file(self, f)

    def __str__(self):
        return 'override: {}\talarm: {}\tstart: {}\tend: {}'.format(self.override, self.alarm, self.godzina_start,
                                                                    self.godzina_end)

# TODO jakis blad, kiedy OVERRIDE jest na start, to wtedy nie moze sie polaczyc baza?
