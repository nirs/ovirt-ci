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

cfg = config.load()

ga = gerrit.API(host=cfg.gerrit.host)

ja = jenkins.API(
    host=cfg.jenkins.host,
    user_id=cfg.jenkins.user_id,
    api_token=cfg.jenkins.api_token)

out = output.TextOutput(steps=8)

out.step("Getting build info for change %s", change)
info = ga.build_info(change)

out.step("Starting build-artifacts job")
out.info(("project", info["project"]),
         ("branch", info["branch"]),
         ("patchset", info["patchset"]))
queue_url = ja.run(
    url=info["url"], ref=info["ref"], stage="build-artifacts")

out.step("Waiting for queue item %s", queue_url)
job_url = ja.wait_for_queue(queue_url)

out.step("Waiting for job %s", job_url)
result = ja.wait_for_job(job_url)

if result != "SUCCESS":
    out.failure("Build artifacts %s failed", job_url)
    sys.exit(1)

out.step(
    "Starting oVirt system tests %s suite with custom repos %s",
    suite_type, job_url)
queue_url = ja.build(
    "ovirt-system-tests_manual",
    parameters={
        "CUSTOM_REPOS": job_url,
        "ENGINE_VERSION": engine_version,
        "SUITE_TYPE": suite_type,
    }
)

out.step("Waiting for queue item %s", queue_url)
job_url = ja.wait_for_queue(queue_url)

out.step("Waiting for job %s", job_url)
result = ja.wait_for_job(job_url)

if result != "SUCCESS":
    out.failure("System tests failed with: %s", result)
    sys.exit(1)

out.success("System tests completed successfully, congratulations!")
