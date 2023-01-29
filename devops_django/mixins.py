
import json
import datetime

from tablib import Dataset

from django.http.response import HttpResponse
from django.db import models
from django.core import exceptions as django_exceptions

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import decorators
from rest_framework import serializers

from . import decorators as hb_decorators
from . import models as hb_model
from . import metadata as hb_metadata


class ExportMixin(object):

    metadata_class = hb_metadata.ExportSimpleMetadata

    CONTENT_TYPE_MAP = {
        "xls": "application/vnd.ms-excel",
        "csv": "text/csv",
        "json": "application/json",
        "html": "text/html"
    }

    @action(methods=['get'], detail=False, url_path='export')
    @hb_decorators.parameter("_format", str, default="xls", choices=("xls", "csv", "json", "html"))
    @hb_decorators.parameter("_field", str, True, default=[])
    def export(self, request, _format, _field, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        data = Dataset()
        serializer_class = self.get_serializer_class()()
        all_field_names = serializer_class.fields.fields.keys()
        export_field_names = all_field_names
        if _field:
            not_exist_fields = set(_field) - all_field_names
            if not_exist_fields:
                raise exceptions.ParseError(f"未知字段: {','.join(not_exist_fields)}")
            export_field_names = _field
        headers = [serializer_class.fields[field_name].label for field_name in export_field_names]
        data.headers = headers
        for i in serializer.data:
            item = [str(i[name]) if name in i else None for name in export_field_names]
            data.append(item)
        response = HttpResponse(getattr(data, _format), content_type=self.CONTENT_TYPE_MAP[_format])
        full_path = request.get_full_path()
        query_params_str = ""
        if len(full_path.split("?")) > 1:
            query_params_str = full_path.split("?")[-1]
        time_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = "{}-{}-{}.{}".format(self.__class__.__name__, query_params_str[0:150], time_str, _format)
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        return response


class CountMixin:

    @action(methods=["get"], detail=False, url_path="count")
    def count(self, request, *args, **kwargs):
        count = self.filter_queryset(self.get_queryset()).count()
        return Response({"count": count})


class AggregationMixin:

    FUNC_MAP = {
        "count": models.Count,
        "avg": models.Avg,
        "sum": models.Sum,
        "max": models.Max,
        "min": models.Min,
    }

    @action(methods=["get"], detail=False, url_path="aggregation")
    @hb_decorators.parameter(name="_column", _type=str, is_multi=False, default="id")    #_column 对那个字段统计
    @hb_decorators.parameter(name="_func", _type=str, choices=("count", "avg", "sum", "max", "min"))    #使用什么函数统计
    def aggregation(self, request, _func, _column):
        queryset = self.get_queryset()
        model = queryset.model
        field_names = hb_model.get_all_field_name(model)
        if _column not in field_names:
            raise exceptions.ParseError("参数_column必须为{}之一".format(field_names))
        queryset = self.filter_queryset(queryset)
        kwargs = {_func: self.FUNC_MAP[_func](_column)}
        data = queryset.aggregate(**kwargs)
        return Response(data)


class GroupByMixin:

    FUNC_MAP = {
        "count": models.Count,
        "avg": models.Avg,
        "sum": models.Sum,
        "max": models.Max,
        "min": models.Min,
    }

    def add_display_field(self, results, model_cls, display_field):
        if not display_field:
            return results
        for result in results:
            for display_field_name in display_field:
                if not display_field_name.endswith("__display"):
                    raise exceptions.ParseError("_display_field必须以__display结尾")
                field_name = display_field_name.split("__display")[0]
                arg = {field_name: result[field_name]}
                result[display_field_name] = getattr(model_cls(**arg), f"get_{field_name}_display")()
        return results

    @action(methods=["get"], detail=False, url_path="group-by")
    @hb_decorators.parameter(name="_column", _type=str, is_multi=True, default=["id"])    #_column 对那个字段统计
    @hb_decorators.parameter(name="_func", _type=str, is_multi=True, choices=("count", "avg", "sum", "max", "min"))    #使用什么函数统计
    @hb_decorators.parameter(name="_value", _type=str, is_multi=True, default=[])                  #用那些字段分组
    @hb_decorators.parameter(name="_display_field", _type=str, is_multi=True, default=[])
    @hb_decorators.parameter(name="ordering", _type=str, is_multi=True, default=None)    #_column 排序
    def group_by(self, request, _value=[], _display_field=[], _func=[], _column=None, ordering=[]):
        if _func and not _column:
            raise exceptions.ParseError("_func和_column必须同时指定")
        queryset = self.get_queryset()
        model = queryset.model
        field_names = hb_model.get_all_field_name(model)
        invalid_values = set(_value) - set(self.group_by_fields)
        if invalid_values:
            raise exceptions.ParseError(f"无效的_value: {invalid_values} _value只能为 {self.group_by_fields}")
        invalid_columns = set(_column) - set(field_names)
        # if invalid_columns:
        #     raise exceptions.ParseError(f"无效的_column: {invalid_columns} _column只能为 {self.field_names}")
        queryset = self.filter_queryset(queryset)
        kwargs = {item[0]: self.FUNC_MAP[item[0]](item[1]) for item in zip(_func, _column)}
        select = {}
        for item in _value:
            if request.query_params.get(item + "__to_char"):
                select[item] = f"to_char({item}, '{request.query_params.get(item+'__to_char')}')"
        if select:
            queryset = queryset.extra(select=select).values(*_value).annotate(**kwargs)
        else:
            queryset = queryset.values(*_value).annotate(**kwargs)
        if ordering:
            queryset = queryset.order_by(*ordering)
        page = self.paginate_queryset(queryset)
        if page is not None:
            res_data = {
                        "count": len(queryset),
                        "results": page
                        }
            self.add_display_field(res_data["results"], queryset.model, _display_field)
        else:
            res_data = list(queryset)
            self.add_display_field(res_data, queryset.model, _display_field)
        return Response(res_data)


class GroupByCountMixin:

    @action(methods=["get"], detail=False, url_path="group-by/count")
    @hb_decorators.parameter(name="_column", _type=str, is_multi=False, default=None)
    @hb_decorators.parameter(name="_func", _type=str, default=None, choices=("count", "avg", "sum", "max", "min"))
    @hb_decorators.parameter(name="_value", is_multi=True, default=None)
    def group_by_count(self, request, _value=None, _func=None, _column=None):
        if _value is None or _func is None or _column is None:
            raise exceptions.ParseError("必须提供_value、_func、_column")
        queryset = self.get_queryset()
        model = queryset.model
        field_names = hb_model.get_all_field_name(model)
        for v in _value:
            if v not in self.group_by_fields:
                raise exceptions.ParseError("参数value必须为{}".format(self.group_by_fields))
        if _column not in field_names:
            raise exceptions.ParseError("参数column必须为{}之一".format(field_names))
        queryset = self.filter_queryset(queryset)
        kwargs = {_func: self.FUNC_MAP[_func](_column)}
        queryset = queryset.values(*_value).annotate(**kwargs)
        queryset = self.group_by_filter_queryset(queryset, _func)
        count = queryset.count()
        data = {"count": count}
        return Response(data)


class IdToDateFormatMixin:

    def perform_create(self, serializer):
        queryset = self.get_queryset()
        today_string = datetime.datetime.now().strftime("%y%m%d")
        try:
            last_instance = queryset.order_by("-id")[0]
        except IndexError:
            index = 1
        else:
            id_date_string = str(last_instance.id)[:6]
            if today_string == id_date_string:
                index = int(str(last_instance.id)[6:]) + 1
            else:
                index = 1
        index_string = "%04d"%index
        id = int(today_string + index_string)
        serializer.save(id=id)


class ChoiceMixin:
    s = serializers.Serializer()
    s.__init__()

    class Serializer(serializers.Serializer):

        def __init__(self, model, data):
            self.model = model
            super().__init__(data=data)

        field_name = serializers.CharField()

        def validate_field_name(self, value):
            try:
                field = self.model._meta.get_field(value)
            except django_exceptions.FieldDoesNotExist as exc:
                raise exceptions.ValidationError(str(exc))
            if not hasattr(field, "choices"):
                raise exceptions.ValidationError(f"field {value} is not choices field")
            return value

    @decorators.action(methods=["get"], detail=False, url_path="get-choices", url_name="get-choices")
    def get_choices(self, request, *args, **kwargs):
        # if not field_name:
        #     raise exceptions.ParseError("必须指定field_name")
        queryset = self.get_queryset()
        model = queryset.model

        serializer = self.Serializer(model, request.query_params)
        serializer.is_valid(raise_exception=True)
        field_name = serializer.validated_data["field_name"]
        choices = model._meta.get_field(field_name).choices
        results = [{"value": item[0], "label": item[1]} for item in choices]
        label_value_map = {label: value for value, label in choices}
        value_label_map = {value: label for value, label in choices}

        data = {
            "count": len(choices),
            "results": results,
            "label_value_map": label_value_map,
            "value_label_map": value_label_map
        }
        return Response(data)
