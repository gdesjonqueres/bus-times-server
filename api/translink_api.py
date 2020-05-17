from tools.http_request import HTTPRequest


class TranslinkApi:
    """Translink Api client

    """
    base_url = 'https://api.translink.ca/rttiapi/v1/'
    timezone = 'America/Vancouver'

    def __init__(self, api_key, return_request_only=False):
        self.api_key = api_key
        self.request_only = return_request_only

    def _build_request(self, resource, parameters={}):
        url = self.base_url + resource
        parameters['apikey'] = self.api_key
        request = HTTPRequest(url, parameters).set_accept_json()
        return request

    def _do_request(self, resource, parameters={}):
        request = self._build_request(resource, parameters)
        if self.request_only:
            return request
        return request.send().json()

    def get_stop(self, stop_code):
        return self._do_request(f'stops/{stop_code}')

    def get_estimates(self, stop_code, route_code=None, time_frame=40):
        params = {}
        if route_code:
            params['routeNo'] = route_code
        if time_frame:
            params['timeFrame'] = time_frame
        return self._do_request(f'stops/{stop_code}/estimates', params)

    def get_route(self, route_code):
        return self._do_request(f'routes/{route_code}')

    def get_routes_at_stop(self, stop_code):
        return self._do_request('routes', {'stopNo': stop_code})
