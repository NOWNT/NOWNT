from enum import Enum
from datetime import datetime
from urllib.parse import urlencode
import requests


# Enumeration for http methods
class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


# Abstract task class
class Task:
    endpoint = ""
    method: HttpMethod = None
    body = {}
    form_data = {}
    query_string_params = []

    def request(self, hostname):
        if self.body and self.form_data:
            raise ValueError("Can't use body with form_data simultaneously.")

        url = hostname + '/' + self.endpoint

        if self.query_string_params:
            url += '?'
            url += urlencode(self.query_string_params, doseq=True)

        request_start_time = datetime.now().timestamp()
        response = None
        if self.method == HttpMethod.GET:
            response = requests.get(url=url, timeout=5)
        elif self.method == HttpMethod.POST:
            if self.form_data:
                response = requests.post(url=url, data=self.body, timeout=5)
            else:
                response = requests.post(url=url, files=self.form_data, timeout=5)
        elif self.method == HttpMethod.PUT:
            if self.form_data:
                response = requests.put(url=url, data=self.body, timeout=5)
            else:
                response = requests.put(url=url, files=self.form_data, timeout=5)
        elif self.method == HttpMethod.DELETE:
            response = requests.delete(url=url)

        result = {
            'endpoint': self.endpoint,
            'start_timestamp': request_start_time,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds()
        }

        return result
