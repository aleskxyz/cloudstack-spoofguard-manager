import hashlib, hmac, base64, urllib, json
import requests
import urllib3
urllib3.disable_warnings()

class CloudStackClient():
    def __init__(self, api_url, apiKey, secret):
        self.api_url = api_url
        self.apiKey = apiKey
        self.secret = secret

    def request(self, args):
        args['apiKey'] = self.apiKey

        self.params = []
        self._sort_request(args)
        self._create_signature()
        self._build_post_request()

    def _sort_request(self, args):
        keys = sorted(args.keys())

        for key in keys:
            self.params.append(key + '=' + urllib.parse.quote_plus(args[key]))

    def _create_signature(self):
        self.query = '&'.join(self.params)
        digest = hmac.new(
            self.secret.encode('utf-8'),
            msg=self.query.lower().encode('utf-8'),
            digestmod=hashlib.sha1).digest()

        self.signature = base64.b64encode(digest)

    def _build_post_request(self):
        self.query += '&signature=' + urllib.parse.quote_plus(self.signature)
        self.value = self.api_url + '?' + self.query

    def __getattr__(self, name):
        def handlerFunction(*args, **kwargs):
            if kwargs:
                return self._make_request(name, kwargs)
            return self._make_request(name, args[0])
        return handlerFunction

    def _http_get(self, url):
        response = requests.request('GET', url , verify = False)
        response.raise_for_status()
        return response.text

    def _make_request(self, command, args):
        args['response'] = 'json'
        args['command'] = command
        self.request(args)
        data = self._http_get(self.value)
        # The response is of the format {commandresponse: actual-data}
        key = command.lower() + "response"
        return json.loads(data)[key]