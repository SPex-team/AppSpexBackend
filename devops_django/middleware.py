import json
import logging
import traceback

from django.http.response import HttpResponse
from django.conf import settings

logger = logging.getLogger("exception")
request_logger = logging.getLogger("request")


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if settings.DEBUG:
            raise exception
        data = {
            "detail": str(exception)
        }
        logger.error(traceback.format_exc())
        return HttpResponse(json.dumps(data), status=500)


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return response
        if not request.path.startswith("/api/"):
            return response
        data = {
            "request_method": request.method,
            "request_url": request.path,
            "request_body": request.body.decode(),
            "response_status": response.status_code,
            "response_content": response.content.decode()
        }
        log_content = json.dumps(data)
        request_logger.debug(log_content)
        return response

