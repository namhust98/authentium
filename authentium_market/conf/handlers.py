from django.http import JsonResponse
from rest_framework.views import exception_handler
from .exceptions import APIException
from django.core.paginator import Page


def json_response(data=None, status_code=200, pagination=None):

    response_data = {}
    if data is not None:
        response_data['data'] = data

    if pagination is not None and isinstance(pagination, Page):
        response_data['pagination'] = {
            'page': pagination.number,
            'per_page': pagination.paginator.per_page,
            'num_pages': pagination.paginator.num_pages,
            'total': pagination.paginator.count
        }

    return JsonResponse(data=response_data, status=status_code)


def api_exception_handler(exc, context):

    # https://stackoverflow.com/questions/60426446/global-exception-handling-in-django-rest-framework
    response = exception_handler(exc, context)

    if isinstance(exc, APIException):
        err_data = {
          'code': exc.code,
          'title': exc.title,
          'detail': exc.detail
        }
        response_data = {'errors': err_data}

        return JsonResponse(data=response_data, safe=False, status=exc.code)

    return response