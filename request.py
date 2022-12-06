import random

import requests.utils
from diskcache import Cache


class Request:

    def __init__(self, **kwargs):
        self.use_cache = kwargs.get('use_cache', False)
        self.cache = Cache(directory='/../requestCache')
        user_agent_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36'
        ]
        self.headers = {'User-Agent': random.choice(user_agent_list)}

    def do_request(self, url):
        response = None
        if self.use_cache:
            response = self.cache.get(url)
        if response:
            print('get response form cache')
        else:
            try:
                response = requests.get(url, headers=self.headers, verify=False)
            except Exception as e:
                print(e)
                return None

        if response.status_code not in range(200, 209):
            print('request error')
            return None

        response.encoding = response.apparent_encoding
        self.cache.set(url, response, expire=24 * 60 * 60 * 7)
        return response


