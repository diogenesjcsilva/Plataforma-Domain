from core.component import Component


class Translator(Component):
    def __init__(self, index):
        Component.__init__(self)
        self.index = index

    def to_domain(self, app_id, mapped):
        """ converts mapped data to domain data """
        if not "_metadata" in mapped:
            return mapped.copy()
        map_type = mapped['_metadata']['type']
        _map = self.index.get_map_by_app_id_and_name(app_id, map_type)
        translated = dict()
        translated['_metadata'] = mapped['_metadata']
        translated['_metadata']['type'] = _map['model']
        _list = self.index.columns_from_map_type(app_id, map_type)
        for replacement in _list:
            _from = replacement[0]
            _to = replacement[1]
            if _from in mapped:
                translated[_to] = mapped[_from]
        return translated

    def to_map(self, app_id, mapped):
        """ convert domain object to mapped object """
        if not "_metadata" in mapped:
            return mapped.copy()
        map_type = self.index.get_map_type_by_domain_type(
            app_id, mapped['_metadata']['type'])
        _map = self.index.get_map_by_app_id_and_name(app_id, map_type)
        translated = dict()
        translated['_metadata'] = dict()
        translated['_metadata']['type'] = map_type
        _list = self.index.columns_from_map_type(app_id, map_type)
        for replacement in _list:
            _from = replacement[1]
            _to = replacement[0]
            if mapped[_from]:
                translated[_to] = mapped[_from]
        return translated