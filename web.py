import time

from flask import Flask, render_template, request, redirect
import psutil
import datetime

old_bytes_sent = 0
new_bytes_sent = 0

end_datetime = None


def launch_web(host, port, test, database, duration=None):
    app = Flask(__name__)

    def convert_to_mbit(value):
        return round(value / 1024. / 1024. * 8, 2)

    def calculate_bandwidth():
        global old_bytes_sent
        global new_bytes_sent

        new_bytes_sent = psutil.net_io_counters().bytes_sent
        bandwidth = new_bytes_sent - old_bytes_sent
        old_bytes_sent = new_bytes_sent
        if old_bytes_sent:
            return convert_to_mbit(bandwidth)
        return 0

    @app.route("/")
    def home():
        for user in test.users:
            if not user.stopped[0]:
                return redirect('/results')
        return render_template('new-index.html')

    @app.route("/start", methods=['POST'])
    def start():
        global end_datetime
        for user in test.users:
            if not user.stopped[0]:
                return redirect('/results')

        test.hostname = request.form['hostname']
        if duration:
            end_datetime = datetime.datetime.now() + datetime.timedelta(seconds=duration)
        test.start()
        calculate_bandwidth()

        return redirect('/results')

    @app.route("/results")
    def results():
        all_results = []
        try:
            tag = test.tag
        except:
            tag = ""

        for user in test.users:
            all_results.extend(user.results)

        if end_datetime and datetime.datetime.now() > end_datetime:
            return redirect('/stop')

        all_response_times = [result["response_time"] for result in all_results]
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory()[2]

        return render_template('new-results.html', **{
            'results': all_results,
            'hostname': test.hostname,
            'tag': tag,
            'num_users': sum(test.user_map.values()),
            'avg_response_time': round(
                sum(all_response_times) / (len(all_response_times) if len(all_response_times) > 0 else 1), 2) * 1000,
            'ram_usage': ram_usage,
            'cpu_usage': cpu_usage
        })

    @app.route("/stop")
    def stop():
        test.stop(calculate_bandwidth(), database=database)
        return redirect('/')

    @app.route("/previous")
    def previous():
        for user in test.users:
            if not user.stopped[0]:
                return redirect('/results')
        hostnames = database.get_all_hostnames()
        tests = database.get_all_tests()[::-1]
        all_requests = database.get_all_requests()
        statuses = {
            t[2]: {
                "success": len([r for r in all_requests if r[5] == t[2] and r[6] == 200]),
                "fail": len([r for r in all_requests if r[5] == t[2] and r[4] == 200])
            }
            for t in tests
        }
        tests = [
            (
                t[0],
                t[1],
                t[2],
                round((
                        datetime.datetime.fromtimestamp(float(t[4])) - datetime.datetime.fromtimestamp(float(t[3]))
                ).total_seconds(), 2),
                t[5],
                t[6],
                database.get_average_response_time(t[2]),
                t[8],
                next((h[0] for h in hostnames if t[7] == h[1]), '-'))
            for t in tests
        ]
        return render_template('new-previous.html', **{'tests': tests, "statuses": statuses})

    app.run(host=host, port=port, debug=True)
