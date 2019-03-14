import json
from six.moves import http_client


class Error(Exception):
    pass


class API(object):

    # To prevent against Cross Site Script Inclusion (XSSI) attacks, the JSON
    # response body starts with a magic prefix line that must be stripped
    # before feeding the rest of the response body to a JSON parser.
    MAGIC_PREFIX = b")]}'\n"

    def __init__(self, host):
        self.host = host
        self._con = http_client.HTTPSConnection(host)

    def build_info(self, change_num):
        """
        Return information requiref for building the current reviesion of a
        patch in jenkins.
        """
        url = "/changes/?q={}&o=CURRENT_REVISION".format(change_num)
        res = self._request("GET", url)[0]

        cur_rev = res["current_revision"]
        ref = res["revisions"][cur_rev]["ref"]
        url = res["revisions"][cur_rev]["fetch"]["git"]["url"]

        return {"ref": ref, "url": url}

    def _request(self, method, url):
        self._con.request(method, url)
        res = self._con.getresponse()
        body = res.read()
        if res.status != http_client.OK:
            raise Error("Request failed status=%r body=%r", res.status, body)

        if body.startswith(self.MAGIC_PREFIX):
            body = body[len(self.MAGIC_PREFIX):]

        return json.loads(body)
