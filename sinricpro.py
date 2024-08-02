from sinric import SinricPro, SinricProConstants
import asyncio
import os
from threading import Thread
from loguru import logger

class SinricproConnection:
    def __init__(self,on_power_state=lambda: None):
        self._on_power_state = on_power_state
        _file = os.path.abspath(__file__)
        _parent = os.path.dirname(_file)
        _sinric_pro_login_file = os.path.join(_parent, 'sinricpro_login.txt')
        self._client = None
        self._thread = None
        try:
            with open(_sinric_pro_login_file, 'r') as f:
                lines = f.readlines()
            self._APP_KEY = lines[0].strip()
            self._APP_SECRET = lines[1].strip()
            self._SWITCH_ID = lines[2].strip()
            self._do_connect = True
        except FileNotFoundError:
            logger.warning("Nie połączono z usługą SinricPro.")
            self._do_connect = False

    def start(self):
        if self._do_connect:
            callbacks = {
                SinricProConstants.SET_POWER_STATE: self._power_state
            }

            self._client = SinricPro(self._APP_KEY, [self._SWITCH_ID], callbacks,
                                     enable_log=False, restore_states=False, secret_key=self._APP_SECRET)

            self._thread = Thread(target=self._callback, name="szafa_sinricpro")
            self._thread.daemon = True
            self._thread.start()
            return self._client

    def _power_state(self, device_id, state):
        logger.info(f"Received SinricPro state:\t{state}")
        self._on_power_state(True)
        return True, state

    @logger.catch
    def _callback(self):
        if self._do_connect:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._client.connect())

    def on(self):
        if self._client is not None:
            self._client.event_handler.raise_event(self._SWITCH_ID, SinricProConstants.SET_POWER_STATE,
                                             data={SinricProConstants.STATE: SinricProConstants.POWER_STATE_ON})

    def off(self):
        if self._client is not None:
            self._client.event_handler.raise_event(self._SWITCH_ID, SinricProConstants.SET_POWER_STATE,
                                             data={SinricProConstants.STATE: SinricProConstants.POWER_STATE_OFF})
##########################


#     # To update the power state on server.
#     # client.event_handler.raise_event(SWITCH_ID, SinricProConstants.SET_POWER_STATE, data = {SinricProConstants.STATE: SinricProConstants.POWER_STATE_ON })
#     # client.event_handler.raise_event(SWITCH_ID, SinricProConstants.SET_POWER_STATE, data = {SinricProConstants.STATE: SinricProConstants.POWER_STATE_OFF })
