import socket
from threading import Thread
import json
from datetime import datetime
import base64
import os

class Server:
    def __init__(self, parent_path, distance_sensor, override=lambda: None, port=80, debug=False):
        _auth_file = os.path.join(parent_path, 'auth.txt')
        if os.path.isfile(_auth_file):
            with open(_auth_file, 'r') as f:
                self.auth = f.read().split('\n')
        else:
            self.auth = None

        print self.auth

        self.override = override
        self.distance_sensor = distance_sensor
        self.debug = debug
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(0.2)
        self.s.bind(addr)
        
        self._thread = None
        
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
        print self._thread.is_alive()# if not, start again        

    def start(self):
        self.s.listen(1)
        self._thread = Thread(target=self._callback, name="szafa_server")
        self._thread.daemon = True
        self._thread.start()

    def _callback(self):
        while True:
            try:
                cl, addr = self.s.accept()
                byt = str(cl.recv(4096))
                URL = byt.split()[1]
                if self.debug:
                    print(URL)

                if 'Authorization' in byt or self.auth is None:
                    # Extract the encoded credentials from the header
                    if self.auth is not None:
                        encoded_credentials=filter(lambda x: x.startswith('Authorization'), byt.split('\n'))[0][len('Authorization: Basic '):]
                        # Decode the credentials
                        decoded_credentials = base64.b64decode(encoded_credentials)
                        # Split the credentials into username and password
                        username, password = decoded_credentials.split(':')

                    # Check if the username and password are valid
                    if self.auth is None or (username == self.auth[0] and password == self.auth[1]):
                        if URL == '/':
                            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')

                            temp = 'Zamknieta'

                            if self.info[0] > self.distance_sensor.max_distance:
                                temp = 'Otwarta'

                            override_str = ''

                            if self.info[1]:
                                override_str = 'OV'

                            cl.send(self._html.format(

                                '<h1 style="display: inline;">{} {}</h1> <h3 style="display: inline;">({:.2f} cm)</h3>'.format(
                                    temp, override_str, self.info[0])

                            ))
                            cl.close()
                        elif URL == '/api':
                            cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
                            czas = datetime.now()
                            data = {'czy_nadpis': self.info[1],
                                    'czy_otwarta': self.info[0] > self.distance_sensor.max_distance,
                                    'max_distance': self.distance_sensor.max_distance, 'odleglosc': self.info[0],
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
                    else:
                        # Invalid credentials
                        cl.send(
                            'HTTP/1.0 401 Unauthorized\r\nWWW-Authenticate: Basic realm="Restricted"\r\nContent-type: text/html\r\n\r\n')
                        cl.send('<h1>401 Unauthorized</h1>')
                        cl.close()
                else:
                    cl.send('HTTP/1.0 401 Unauthorized\r\nWWW-Authenticate: Basic realm="Restricted"\r\nContent-type: text/html\r\n\r\n')
                    cl.send('<h1>401 Unauthorized</h1>')
                    cl.close()


            except socket.timeout:
                pass
