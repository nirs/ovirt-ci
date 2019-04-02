import logging
import os
import sys

from oci import config
from oci import gerrit
from oci import jenkins
from oci import output

change = sys.argv[1]

if len(sys.argv) > 2:
    engine_version = sys.argv[2]
else:
    engine_version = "master"

suite_type = "basic"

logging.basicConfig(
    level=logging.DEBUG if "DEBUG" in os.environ else logging.WARNING,
    format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s")

cfg = config.load()

ga = gerrit.API(host=cfg.gerrit.host)

ja = jenkins.API(
    host=cfg.jenkins.host,
    user_id=cfg.jenkins.user_id,
    api_token=cfg.jenkins.api_token)

out = output.TextOutput(steps=8)

# TODO: the build-artifacts flow was copied from build-artifacts.py. Find a way
# to reuse the code instead of copying it.

out.step("Getting build info for change %s", change)
info = ga.build_info(change)

out.step("Starting build-artifacts job")
out.info(("project", info["project"]),
         ("branch", info["branch"]),
         ("patchset", info["patchset"]))
queue_url = ja.run(
    url=info["url"], ref=info["ref"], stage="build-artifacts")

out.step("Waiting until job is executed")
out.info(("queue", queue_url))
job_url = ja.wait_for_queue(queue_url)

out.step("Waiting until job is completed")
out.info(("job", job_url))
result = ja.wait_for_job(job_url)

if result != "SUCCESS":
    out.failure("Build artifacts %s failed", job_url)
    sys.exit(1)

out.step("Starting oVirt system tests job")
out.info(("suite", suite_type), ("repo", job_url))
queue_url = ja.build(
    "ovirt-system-tests_manual",
    parameters={
        "CUSTOM_REPOS": job_url,
        "ENGINE_VERSION": engine_version,
        "SUITE_TYPE": suite_type,
    }
)

out.step("Waiting until job is executed")
out.info(("queue", queue_url))
job_url = ja.wait_for_queue(queue_url)

out.step("Waiting until job is completed")
out.info(("job", job_url))
result = ja.wait_for_job(job_url)

if result != "SUCCESS":
    out.failure("System tests failed with: %s", result)
    sys.exit(1)

out.success("System tests completed successfully, congratulations!")
