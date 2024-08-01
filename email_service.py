import smtplib, ssl, time, threading, datetime


class SMTPService:
    _smtp_server = "smtp.gmail.com"
    _port = 587  # For starttls

    def __init__(self, filename="smtp.txt"):
        self.__working = True
        self.__status = None
        self.__waiting_to_send = False
        self.__open_time = time.time()
        self.__first = True

        self.__try_connect(filename)

    def __try_connect(self, filename="smtp.txt"):
        self.__working = True
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
                self.__sender = lines[0]
                self.__pwd = lines[1]
                self.__receiver = lines[2]
                self.__timer_sec = int(lines[3])

                context = ssl.create_default_context()

                self.server: SMTP = smtplib.SMTP(SMTPService._smtp_server, SMTPService._port)

                self.server.ehlo()  # Can be omitted
                self.server.starttls(context=context)
                self.server.ehlo()  # Can be omitted
                self.server.login(self.__sender, self.__pwd)
        except Exception:
            self.__working = False

    def is_working(self):
        return self.__working

    def send_new_status(self, status) -> bool:
        if not self.__working:
            return False

        self.__status = status
        if self.__waiting_to_send:
            self.__waiting_to_send = False
            return False

        self.__waiting_to_send = True
        threading.Thread(target=self.__thread_send).start()
        return True

    def __thread_send(self):
        time.sleep(self.__timer_sec)
        debug = False
        if self.__waiting_to_send:
            # if self.__open_time == -1:
            #     self.__send(-1, debug=debug)
            # else:
            self.__send(time.time() - self.__open_time, debug=debug)
            self.__open_time = time.time()
            self.__waiting_to_send = False
        else:
            print("Przestano wysyłac")

    def __send(self, time_sec, debug=True):
        subject = "Szafa - informacja"

        time_sec_info = str(datetime.timedelta(seconds=time_sec))

        if self.__first:
            time_sec_info += " (PIERWSZA INFORMACJA)"
            self.__first = False

        if self.__status:
            status = "Została otwarta. Była zamknięta przez: "
        else:
            status = "Została zamknięta. Była otwarta przez: "
        message = f"{datetime.datetime.now():%m-%d %H:%M:%S}: {status}{time_sec_info}"
        if debug:
            self.__send_debug(subject, message)
        else:
            self.__send_email(subject, message)

    def __send_email(self, subject="Hi there", message="Test message", try_time=0) -> bool:
        if not self.__working:
            return False

        if try_time > 0:
            print(f"\t\tŁącze po raz:\t{try_time}")
            self.__try_connect("smtp.txt")

        try:
            self.server.sendmail(self.__sender, self.__receiver, f"Subject: {subject}\n\n{message}".encode('utf-8'))
        except Exception as e:
            print(e)
            print("Probuje ponownie...")
            self.close()
            self.__working = True
            self.__send_email(subject, message, try_time + 1)
        return True

    def __send_debug(self, subject="Hi there", message="Test message") -> bool:
        if not self.__working:
            return False
        print(f"Subject: {subject}:::{message}")
        return True

    def close(self) -> bool:
        if self.__working:
            try:
                self.server.quit()
            except Exception as e:
                pass
            self.server = None
            self.__working = False
            return True
        return False


if __name__ == "__main__":
    smtp = SMTPService()
    otwarta = False
    while True:
        if otwarta:
            print("OTWARTA")
        else:
            print("ZAMKNIETA")

        _ = input()
        smtp.send_new_status(otwarta)
        otwarta = not otwarta

