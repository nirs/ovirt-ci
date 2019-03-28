import logging
import sys

from oci import config
from oci import gerrit
from oci import jenkins
from oci import output

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s")

log = logging.getLogger("build-artifacts")

change = sys.argv[1]

cfg = config.load()

ga = gerrit.API(host=cfg.gerrit.host)

ja = jenkins.API(
    host=cfg.jenkins.host,
    user_id=cfg.jenkins.user_id,
    api_token=cfg.jenkins.api_token)

output.info("[ 1/5 ] Getting build info for change %s", change)
info = ga.build_info(change)

output.info("[ 2/5 ] Starting build-artifacts job for %s", info)
queue_url = ja.run(
    url=info["url"], ref=info["ref"], stage="build-artifacts")

output.info("[ 3/5 ] Waiting for queue item %s", queue_url)
job_url = ja.wait_for_queue(queue_url)

output.info("[ 4/5 ] Waiting for job %s", job_url)
result = ja.wait_for_job(job_url)

if result != "SUCCESS":
    output.failure("[ 5/5 ] Build artifcats failed with %s", result)
    sys.exit(1)

output.success("[ 5/5 ] Job completed successfuly, congragulations!")
