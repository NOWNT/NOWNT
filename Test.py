import datetime
import psutil


class Test:
    hostname = ""
    code = ""
    user_map = {}
    users = []

    def __init__(self):
        self.start_datetime = None
        self.end_datetime = None

    def start(self):
        self.start_datetime = datetime.datetime.now().timestamp()
        for user, count in self.user_map.items():
            for i in range(count):
                user_instance = user()
                user_instance.start(self.hostname)
                self.users.append(user_instance)

    def stop(self, bandwidth, database=None):
        self.end_datetime = datetime.datetime.now().timestamp()
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory()[2]

        for user in self.users:
            try:
                user.stop()
            except:
                pass

        if database:
            hostname = next((h for h in database.get_all_hostnames() if self.hostname == h[0]), None)
            if not hostname:
                hostname = (self.hostname, database.store_hostname(self.hostname))

            user_count = 0
            for key, value in self.user_map.items():
                user_count += value

            test_id = database.store_test(
                self.code, user_count, self.start_datetime, self.end_datetime, cpu_usage, ram_usage, hostname[1], bandwidth
            )

            for user in self.users:
                results = user.results
                user.results = []
                for result in results:
                    database.store_request(
                        result['endpoint'],
                        result['start_timestamp'],
                        result['response_time'],
                        True,
                        result['status_code'], test_id
                    )
