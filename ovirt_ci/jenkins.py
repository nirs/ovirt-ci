import base64
import json
import logging
import time

from contextlib import closing

from six.moves import http_client
from six.moves.urllib import parse as url_parse

from . import network

log = logging.getLogger("jenkins")


class Error(Exception):
    """ General Jeknins error """


class Timeout(Error):
    """ Timeout expired """


class API(object):

    def __init__(self, host, user_id, api_token, timeout=20):
        self.host = host
        self.timeout = timeout
        self._user_id = user_id
        self._api_token = api_token

    def run(self, url=None, ref=None, stage=None):
        """
        Build stage with specified ref for the project identified by url.

        Return a URL to the Jenkins queue item. The caller need to monitor this
        URL to discover the acutal job URL.
        """
        params = {}
        if url:
            params["STD_CI_CLONE_URL"] = url
        if ref:
            params["STD_CI_REFSPEC"] = ref
        if stage:
            params["STD_CI_STAGE"] = stage

        return self.build("standard-manual-runner", parameters=params)

    def system_tests(self, custom_repos=None, engine_version="master",
                     suite_type="basic"):
        """
        Run oVirt system tests manual job.

        Arguments:
            custom_repos (str): build-artifacts job URL for project used in
                oVirt system tests, or yum repo URL (rec:https://...) with the
                pakcages that should be used in this run.
            engine_version (str): Engine version to use for this run. For available
                versions see ENGINE_VERSION popup menu at:
                https://jenkins.ovirt.org/job/ovirt-system-tests_manual/build
            suite_type (str): Suite type to run. For available suite types see
                SUITE_TYPE popup menu at:
                https://jenkins.ovirt.org/job/ovirt-system-tests_manual/build

        Return a URL to the Jenkins queue item. The caller need to monitor this
        URL to discover the acutal job URL.
        """
        params = {}
        if custom_repos:
            # TODO: Support multiple repos.
            params["CUSTOM_REPOS"] = custom_repos
        if engine_version:
            params["ENGINE_VERSION"] = engine_version
        if suite_type:
            params["SUITE_TYPE"] = suite_type

        return self.build("ovirt-system-tests_manual", parameters=params)

    @network.retry()
    def build(self, job_name, parameters=None):
        """
        Build job_name with optional parameters.

        Return a URL to the Jenkins queue item. The caller need to monitor this
        URL to discover the acutal job URL.
        """
        if parameters:
            url = "/job/{}/buildWithParameters".format(job_name)
            body = url_parse.urlencode(parameters)
        else:
            url = "/job/{}/build".format(job_name)
            body = ""

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic {}".format(self._basic_credentials())
        }

        con = http_client.HTTPSConnection(self.host, timeout=self.timeout)
        with closing(con):
            log.debug("POST host=%s url=%s body=%r headers=%s",
                      self.host, url, body, headers)
            con.request("POST", url, body=body, headers=headers)

            res = con.getresponse()
            if res.status != http_client.CREATED:
                raise Error(
                    "Request failed host={} url={} reason={} body={!r}"
                    .format(self.host, url, res.reason, res.read()))

            log.debug("CREATED headers=%s", res.getheaders())
            return res.getheader("location")

    @network.retry()
    def wait_for_queue(self, url, interval=1, timeout=None):
        """
        Wait until queue item idenfied by url is executed.

        I did not find documention for this, but watching the queue JSON API
        during builds show the following steps:

        1. Item is blocked.

            {
              "blocked": True.
              "why": null
            }

        2. Waiting for available executor - this can take minutes for
           system tests job.

            {
              "blocked": False
              "why" : "Waiting for next available executor..."
            }

        3. Job is executing. We should continue to watch the job using the
           executable url, since the queue item will removed after couple of
           minutes.

            {
              "blocked": False,
              "executable": {
                "url": "http://jenkins.ovirt.org/job/name/4330/"
              }
              "why": null
            }

        Return the executing job URL.
        """
        url = url_parse.urlparse(url)
        item_status = url.path + "/api/json?tree=executable[url],blocked,why"

        def job_started(status):
            return not status["blocked"] and "executable" in status

        status = self._wait_for(
            job_started,
            url.netloc,
            item_status,
            interval=interval,
            timeout=timeout)

        return status["executable"]["url"]

    @network.retry()
    def wait_for_job(self, url, interval=10, timeout=None):
        """
        Wait until job idenfied by url is finished.

        Return "SUCCESS" if job was successful, otherwise "FAILURE".
        """
        url = url_parse.urlparse(url)
        job_status = url.path + "/api/json?tree=building,result"

        def job_completed(status):
            return not status["building"]

        status = self._wait_for(
            job_completed,
            url.netloc,
            job_status,
            interval=interval,
            timeout=timeout)

        return status["result"]

    def _wait_for(self, cond, host, url, interval, timeout=None):
        """
        Preform a JSON API GET request with url, and check returned JSON with
        the provided cond function. If cond returns True, return the parsed
        JSON to the caller.

        cond is a function accepting status dict and returning True or False.

        Repeat the check every interval seconds, until cond returns True of
        timeout expires.

        Return status dict returned by Jenkins.
        """
        if timeout:
            deadline = time.time() + timeout

        con = http_client.HTTPSConnection(host, timeout=self.timeout)
        with closing(con):
            while True:
                log.debug("GET host=%s url=%s", host, url)
                con.request("GET", url)

                res = con.getresponse()
                body = res.read()
                if res.status != http_client.OK:
                    raise Error(
                        "Request failed host={} url={} reason={} body={!r}"
                        .format(host, url, res.reason, body))

                log.debug("OK headers=%s body=%r", res.getheaders(), body)
                status = json.loads(body)
                if cond(status):
                    return status

                if timeout and time.time() > deadline:
                    raise Timeout(
                        "Timeout waiting for host={} url={}".format(host, url))

                time.sleep(interval)

    def _basic_credentials(self):
        """
        Return HTTP Basic Authentication credentials string.
        See https://tools.ietf.org/html/rfc2617

        To allow unicode user_id and password, we must encode the credentials
        using UTF-8. This encoding is not specified by the RFC, but it is the
        only encoding that can work for unicode. Because UTF-8 is compatible
        with US-ASCII, non-unicode values are passed correctly.
        """
        credentials = "{}:{}".format(self._user_id, self._api_token)
        return base64.b64encode(credentials.encode("utf-8")).decode("ascii")
