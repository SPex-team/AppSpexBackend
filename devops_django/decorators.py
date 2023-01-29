
import datetime
import functools


from rest_framework import exceptions


def parameter(name, _type=str, is_multi=False, required=True, default=None, choices=()):
    def decorator(func):
        @functools.wraps(func)
        def inner(self, request, *args, **kwargs):
            if name in request.query_params:
                if is_multi:
                    values = request.query_params.getlist(name)
                    valid_values = []
                    for v in values:
                        try:
                            value = _type(v)
                            if not choices:
                                valid_values.append(value)
                                continue
                            if value in choices:
                                valid_values.append(value)
                        except Exception:
                            continue
                    if valid_values:
                        kwargs[name] = valid_values
                    else:
                        kwargs[name] = default
                else:
                    value = request.query_params.get(name)
                    try:
                        value = _type(value)
                        if choices and value not in choices:
                            value = default
                    except Exception as exc:
                        value = default
                    kwargs[name] = value
            else:
                if required is True:
                    raise exceptions.ParseError(f"Parameter {name} is required")
                kwargs[name] = default
            response = func(self, request, *args, **kwargs)
            return response
        return inner
    return decorator


def parameter_datetime(name, format="%Y-%m-%dT%H:%M:%S", is_multi=False, required=True, default=None):
    def decorator(func):
        def inner(self, request, *args, **kwargs):
            if name in request.query_params:
                if is_multi:
                    values = request.query_params.getlist(name)
                    valid_values = []
                    for v in values:
                        try:
                            value = datetime.datetime.strptime(v, format)
                        except Exception as exc:
                            raise exceptions.ParseError(f"参数{name}错误 {exc}")
                        valid_values.append(value)
                        continue
                    kwargs[name] = valid_values
                else:
                    value = request.query_params.get(name)
                    try:
                        value = datetime.datetime.strptime(value, format)
                    except Exception as exc:
                        raise exceptions.ParseError(f"参数{name}错误 {exc}")
                    kwargs[name] = value
            else:
                if required:
                    raise exceptions.ParseError(f"参数{name}必须指定")
                kwargs[name] = default
            response = func(self, request, *args, **kwargs)
            return response
        return inner
    return decorator
