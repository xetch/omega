from werkzeug.wrappers import Request, Response
from whizbang.http.views import View, TemplateView, StaticFileView
from werkzeug.routing import Map, Rule

class WebApplication(object):
    def __init__(self, name):
        self.name = name
        self.url_map = Map([Rule('/static/<path:file_path>', endpoint='static')])
        self._routes = {'static': StaticFileView()}

    def page(self, endpoint, template_name):
        name = template_name.split('.')[0]
        self.url_map.add(Rule(endpoint, endpoint=name))
        self._routes[name] = TemplateView(template_name)

    def resource(self, name, endpoint):
        self.url_map.add(Rule(endpoint, endpoint=name))
        self._routes[name] = View(name, endpoint)

    def dispatch_request(self, urls, request):
        response = urls.dispatch(
            lambda e, v: self._routes[e](
                request, **v), catch_http_exceptions=True)
        if isinstance(response, (unicode, str)):
            headers = {'Content-type': 'text/html'}
            return Response(response, headers=headers)
        elif isinstance(response, Response):
            return response
        
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        urls = self.url_map.bind_to_environ(environ)
        response = self.dispatch_request(urls, request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def create_app(name):
    return WebApplication(name)
