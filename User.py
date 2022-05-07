from threading import Thread
from time import sleep


class User:
    wait_time = 0
    tag = ""
    tasks = []

    def __init__(self):
        # "stopped" is in the form of a list to passed by reference.
        self.stopped = [True]

        self.__thread = None
        self.results = []

    def start(self, hostname):
        if self.stopped[0]:
            self.stopped[0] = False
            self.__thread = Thread(target=run, args=(hostname, self.tasks, self.wait_time, self.results, self.stopped))
            self.__thread.start()
        else:
            raise SystemError('User already running.')

    def stop(self):
        if not self.stopped[0]:
            self.stopped[0] = True
        else:
            raise SystemError('User is not running.')


def run(hostname, tasks, wait_time, results, stopped):
    while True:
        for task in tasks:
            result = task.request(task, hostname)
            results.append(result)
            if stopped[0]:
                return
            sleep(wait_time)
