import socket
from threading import Thread
import json
from datetime import datetime

class Server:
    def __init__(self, port=80, debug=False):
        self.debug=debug
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(0.2)
        self.s.bind(addr)
        self._html = """<!DOCTYPE html>
        <html>
            <head>
            <title>Zero!</title>
            </head>
            <body>
                <h1>Hej</h1>
                <h2>{}</h2>
            </body>
        </html>
        """
        self.info=''

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
                    cl.send(self._html.format(self.info))
                    cl.close()
                elif URL == '/api':
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
                    czas = datetime.now()
                    data = {'odleglosc': self.info, 'czas' : [czas.year, czas.month, czas.day, czas.hour, czas.minute, czas.second]}
                    cl.send(json.dumps(data))
                    cl.close()
                else:
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.send("<h1>ERR 404</h1>")
                    cl.close()
            except:
                pass
