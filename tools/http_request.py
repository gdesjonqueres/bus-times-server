import requests


class HTTPRequest:
    """Simple class to perform an HTTP request and hold its state
    """

    def __init__(self, url, parameters={}, headers={}):
        self.url = url
        self.parameters = parameters
        self.headers = headers

    def is_header_set(self, header, value):
        return self.headers.get(header, None) == value

    def set_header(self, header, value):
        self.headers[header] = value
        return self

    def is_parameter_set(self, parameter, value):
        return self.parameters.get(parameter, None) == value

    def set_parameter(self, parameter, value):
        self.parameters[parameter] = value
        return self

    def is_accept_json(self):
        return self.is_header_set('accept', 'application/JSON')

    def set_accept_json(self):
        self.set_header('accept', 'application/JSON')
        return self

    def send(self):
        return requests.get(self.url, headers=self.headers,
                            params=self.parameters)
