import inspect
from parse import parse
from webob import Request, Response
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter


class API:
    # Where to store paths as keys and handlers as values
    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    # Route method, path as an argument
    def route(self, path):
        assert path not in self.routes, "Such route already exists."

        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    # Default response when not found a route
    def default_response(self, response):
        response.status_code = 404
        response.text = "Page Not Found!"

    # Finding a handler
    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named

        return None, None

    # Hanlde request
    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        if handler is not None:
            if inspect.isclass(handler):
                handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    raise AttributeError("Method not allowed", request.method)

            handler(request, response, **kwargs)
        else:
            self.default_response(response)

        return response



    
    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session