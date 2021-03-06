import urllib2
import json

from query import Query

class Pyfire:
    root_data_url = ''
    auth_token = None
    database_secret = ''

    def __init__(self, url, secret):
        self.root_data_url = url if url.endswith('/') else url + '/'
        self.database_secret = secret

    def query(self, endpoint_path):
        return Query(self, endpoint_path)

    def get(self, path, query_params = None):
        return self._execute('GET', path, None, query_params)

    def post(self, path, data, query_params = None):
        res = self._execute('POST', path, data, query_params)

        if not isinstance(res, dict):
            raise Exception('Unexpected return value %s - expected dict' % type(res))

        return res.get('name')

    def put(self, path, data, query_params = None):
        return self._execute('PUT', path, data, query_params)

    def patch(self, path, data, query_params = None):
        return self._execute('PATCH', path, data, query_params)

    def delete(self, path, query_params = None):
        return self._execute('DELETE', path, None, query_params)

    def _execute(self, request_method, path, data, query_params = None):
        request_url = '%s/%s.json?auth=%s%s' % (
            self.root_data_url, path,
            self.database_secret, self._query_string(query_params)
        )

        # Specify the HTTP method using this header to make the code simpler,
        # and because urllib2 only seems to support GET and POST anyway.
        headers = {
            'X-HTTP-Method-Override': request_method.upper()
        }

        if data is not None:
            data = json.dumps(data)
            headers.update({'Content-Type': 'application/json'})

        req = urllib2.Request(request_url, data, headers)
        response = urllib2.urlopen(req).read()

        return json.loads(response)

    def _query_string(self, query_params):
        query_string = ''

        if isinstance(query_params, dict) and len(query_params):
            query_string = '&'
            if query_params.has_key('orderBy'):
                query_string += 'orderBy="%s"' % urllib2.quote(query_params.get('orderBy'))

                # This is nested as you can only use equalTo with orderBy
                if query_params.has_key('equalTo'):
                    query_string += '&equalTo="%s"' % urllib2.quote(query_params.get('equalTo'))

        return query_string

