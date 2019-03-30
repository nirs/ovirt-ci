import json
from six.moves import http_client

# To prevent against Cross Site Script Inclusion (XSSI) attacks, the JSON
# response body starts with a magic prefix line that must be stripped before
# feeding the rest of the response body to a JSON parser.
# https://gerrit-review.googlesource.com/Documentation/rest-api.html#output
_MAGIC_PREFIX = b")]}'\n"


class Error(Exception):
    pass


class API(object):

    def __init__(self, host):
        self.host = host
        self._con = http_client.HTTPSConnection(host)

    def build_info(self, change_num):
        """
        Return information required for building the current revision of
        a patch in Jenkins.
        """
        url = "/changes/?q={}&o=CURRENT_REVISION".format(change_num)
        res = self._request("GET", url)[0]

        cur_rev = res["revisions"][res["current_revision"]]

        return {
            "project": res["project"],
            "branch": res["branch"],
            "patchset": cur_rev["_number"],
            "ref": cur_rev["ref"],
            "url": cur_rev["fetch"]["git"]["url"],
        }

    def _request(self, method, url):
        self._con.request(method, url)
        res = self._con.getresponse()
        body = res.read()
        if res.status != http_client.OK:
            raise Error("Request failed status=%r body=%r", res.status, body)

        if body.startswith(_MAGIC_PREFIX):
            body = body[len(_MAGIC_PREFIX):]

        return json.loads(body)
