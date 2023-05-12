import socket
from threading import Thread
import json
from datetime import datetime

class Server:
    def __init__(self, distance_sensor,override=lambda: None, port=80, debug=False):
        self.override = override
        self.distance_sensor = distance_sensor
        self.debug=debug
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(0.2)
        self.s.bind(addr)
        self._html = """<!DOCTYPE html>
        <html>
            <head>
            <meta charset='utf-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1, shrink-to-fit=no'>
            <title>Zero!</title>
            </head>
            <body style='background-color: gray'>
                {}
                <br>
                <br><hr><br>
                <a href='/api'><button style='padding: 0px 25px'><h2>Api</h2></button></a>
                <br><br>
                <a href='/override'><button style='padding: 0px 25px'><h2>Override</h2></button></a>
            </body>
        </html>
        """
        self.info = (0, False)

    def update(self, info):
        self.info = info

    def start(self):
        self.s.listen(1)
        _t = Thread(target=self._callback)
        _t.daemon = True
        _t.start()
        return _t

    def _callback(self):
        while True:
            try:
                cl, addr = self.s.accept()
                byt = str(cl.recv(4096))
                URL = byt.split()[1]
                if self.debug:
                    print(URL)

                if URL == '/':
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')

                    temp = 'Zamknieta'

                    if self.info[0] > self.distance_sensor.max_distance:
                        temp = 'Otwarta'

                    override_str = ''

                    if self.info[1]:
                        override_str = 'OV'

                    cl.send(self._html.format(

                        '<h1 style="display: inline;">{} {}</h1> <h3 style="display: inline;">({:.2f} cm)</h3>'.format(temp, override_str, self.info[0])

                    ))
                    cl.close()
                elif URL == '/api':
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
                    czas = datetime.now()
                    data = {'czy_nadpis': self.info[1], 'czy_otwarta': self.info[0]>self.distance_sensor.max_distance,
                        'max_distance':self.distance_sensor.max_distance, 'odleglosc': self.info[0],
                            'czas': [czas.year, czas.month, czas.day, czas.hour, czas.minute, czas.second]}
                    cl.send(json.dumps(data))
                    cl.close()
                elif URL == '/override':
                    cl.send('HTTP/1.0 302 OK\r\nLocation: / \r\n\r\n')
                    self.override()
                    cl.close()
                else:
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.send("<h1>ERR 404</h1>")
                    cl.close()
            except:
                pass
