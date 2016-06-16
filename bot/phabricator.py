import requests


class Phabricator:

    def __init__(self, url, api_token):
        self.url = url
        self.api_url = url + '/api'
        self.api_token = api_token

    def convert_data(self, data):
        post_data = dict()
        for key, val in data.items():
            if isinstance(val, list):
                i = 0
                for item in val:
                    post_data['{}[{}]'.format(key, i)] = item
                    i += 1
            else:
                post_data[key] = val
        return post_data

    def run(self, action, args):
        endpoint = self.api_url + '/' + action
        args['api.token'] = self.api_token
        res = requests.post(endpoint, data=self.convert_data(args))

        if res.status_code == 200:
            return res.json()['result']

        return False
