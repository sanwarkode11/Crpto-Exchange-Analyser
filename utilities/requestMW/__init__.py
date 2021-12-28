from threading import current_thread


class GlobalRequest(object):
    _requests = {}

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    @staticmethod
    def get_request():
        try:
            return GlobalRequest._requests[current_thread()]
        except KeyError:
            return None

    def __call__(self, request):
        GlobalRequest._requests[current_thread()] = request
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        # Cleanup                                                               
        thread = current_thread()
        try:
            del GlobalRequest._requests[thread]
        except KeyError:
            pass
        return response


def get_request():
    return GlobalRequest.get_request()
