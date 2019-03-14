import logging
import os
import sys

from six.moves import configparser

from oci import gerrit
from oci import jenkins

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s")

log = logging.getLogger("build-artifacts")

change = sys.argv[1]

config = configparser.ConfigParser()
conf_path =  os.path.expanduser("~/.config/oci.conf")
config.read(conf_path)

ga = gerrit.API(host=config.get("gerrit", "host"))

ja = jenkins.API(
    host=config.get("jenkins", "host"),
    user_id=config.get("jenkins", "user_id"),
    api_token=config.get("jenkins", "api_token"))

log.info("[ 1/5 ] Getting build info for change %s", change)
info = ga.build_info(change)

log.info("[ 2/5 ] Starting build-artifacts job for %s", info)
queue_url = ja.run(
    url=info["url"], ref=info["ref"], stage="build-artifacts")

log.info("[ 3/5 ] Waiting for queue item %s", queue_url)
job_url = ja.wait_for_queue(queue_url)

log.info("[ 4/5 ] Waiting for job %s", job_url)
result = ja.wait_for_job(job_url)

log.info("[ 5/5 ] Job completed with %s", result)
