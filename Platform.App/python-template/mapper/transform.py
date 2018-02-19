from mapper.index import Index
from core.component import Component
import re
import json

class Transform(Component):
    def __init__(self, index):
        Component.__init__(self)
        self.index = index

    def replace_all(self, _from, needle, replacement):
        """ replace all occurences in a string """
        return _from.replace(needle, replacement)

    def replace_all_atributes(self, _from, needle, replacement):
        """ replace json attributes """
        return self.replace_all(_from, "\""+needle+"\":", "\""+replacement+"\":")

    def apply_runtime_fields(self, app_id, map_name, model_list):
        """ apply runtime fields at query result """
        accumulator = dict()
        result = []
        for model in model_list:
            model_json = model.copy()
            model_json['_metadata'] = dict()
            model_json['_metadata']['type'] = map_name
            self.apply_function_fields(
                model_json, app_id, map_name, accumulator)
            self.apply_metadata_fields(model_json)
            result.append(model_json)
        return result

    def apply_function_fields(self, model_json, app_id, map_name, accumulator):
        """ apply function fields """
        if not self.index.has_functions_map(app_id, map_name):
            return model_json

        functions = self.index.get_functions(app_id, map_name)
        for calc_prop in functions:
            if not calc_prop in accumulator:
                accumulator[calc_prop] = dict()
            model_json[calc_prop] = eval(functions[calc_prop]['eval'], {"item":model_json, "accumulator":accumulator[calc_prop]})
        return model_json

    def apply_metadata_fields(self, model_json):
        if "meta_instance_id" in model_json:
            if model_json['meta_instance_id'] != None:
                model_json['_metadata']['instance_id'] = model_json['meta_instance_id']
            model_json.pop('meta_instance_id', None)
        model_json['_metadata']['branch'] = "master"

    def get_filters(self, app_id, map_name, query_string):
        """ apply query filter on domain model """
        filters = self.index.get_filters(app_id, map_name)
        if filters == dict():
            return filters
        if query_string == dict():
            return dict()
        if not query_string["filter"] in filters:
            return dict()
        _filter = filters[query_string["filter"]]

        compiled = re.compile("\$\w*")
        arrays = re.findall(compiled,_filter)

        for item in arrays:
            param = item[1:]
            query_string[param] = query_string[param].split(';')
            _list = []
            for n in query_string[param]:
                if n.isnumeric():
                    _list.append(int(n))
                elif n.replace(".","").isnumeric():
                    _list.append(float(n))
                else:
                    _list.append(n)
            query_string[param] = _list
            _filter = _filter.replace(item,f":{param}")

        return {
            "query" : _filter,
            "params": query_string
        }

