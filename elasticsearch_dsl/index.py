from .connections import connections
from .search import Search

class Index(object):
    def __init__(self, name, using='default'):
        self._name = name
        self._doc_types = {}
        self._mappings = {}
        self._using = 'default'
        self._settings = {}

    def _get_connection(self):
        return connections.get_connection(self._using)
    connection = property(_get_connection)

    def doc_type(self, doc_type):
        name = doc_type._doc_type.name
        self._doc_types[name] = doc_type
        self._mappings[name] = doc_type._doc_type.mapping

        if not doc_type._doc_type.index:
            doc_type._doc_type.index = self._name
        return doc_type # to use as decorator???

    def settings(self, **kwargs):
        self._settings.update(kwargs)
        return self

    def search(self):
        return Search(
            using=self._using,
            index=self._name,
            doc_type=[self._doc_types.get(k, k) for k in self._mappings]
        )

    def _get_mappings(self):
        analysis, mappings = {}, {}
        for mapping in self._mappings.values():
            mappings.update(mapping.to_dict())
            a = mapping._collect_analysis()
            # merge the defintion
            # TODO: conflict detection/resolution
            for key in a:
                analysis.setdefault(key, {}).update(a[key])

        return mappings, analysis

    def to_dict(self):
        out = {}
        if self._settings:
            out['settings'] = self._settings
        mappings, analysis = self._get_mappings()
        if mappings:
            out['mappings'] = mappings
        if analysis:
            out.setdefault('settings', {})['analysis'] = analysis
        return out

    def create(self):
        self.connection.indices.create(index=self._name, body=self.to_dict())

    def delete(self):
        self.connection.indices.delete(index=self._name)