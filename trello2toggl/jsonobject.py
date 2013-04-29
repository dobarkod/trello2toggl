class JSONObject(object):
    """Simple Python object parsed from JSON data

    Makes the code handling a lot of JSON-loaded data easier to write and
    read by converting the JSON to pure Python objects.
    """

    @staticmethod
    def parse(data):
        """Parse a JSON data object (or list of objects) and return a Python
        JSONObject instance (or list of JSONObject instances).

        The input data keys are assumed to all be valid Python identifiers
        """

        if isinstance(data, list):
            return [JSONObject.parse(x) for x in data]

        if isinstance(data, dict):
            o = JSONObject()
            for k, v in data.iteritems():
                if isinstance(v, dict):
                    v = JSONObject.parse(v)
                elif isinstance(v, list):
                    v = [JSONObject.parse(x) for x in v]
                setattr(o, k, v)
            return o

        return data

    def _keys(self):
        return self.__dict__.keys()

    def _get(self, key, dfl=None):
        return self.__dict__.get(key, dfl)
