from functools import lru_cache
from urllib.parse import parse_qs, urlparse



class Request:
    def __init__(self, method, target, version, headers, rfile):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.rfile = rfile

    @property
    def path(self):
        return self.url.path

    @property
    def body(self):
        size = self.headers.get('Content-Length')
        if not size:
            return None
        content = self.rfile.read(int(size))
        return content.decode('utf-8')

    @property
    @lru_cache(maxsize=None)
    def url(self):
        return urlparse(self.target)

    @property
    @lru_cache(maxsize=None)
    def query(self):
        return parse_qs(self.url.query)

    @property
    @lru_cache(maxsize=None)
    def query_body(self):
        return parse_qs(self.body)