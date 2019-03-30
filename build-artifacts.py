import sys

from oci import config
from oci import gerrit
from oci import jenkins
from oci import output

change = sys.argv[1]

cfg = config.load()

ga = gerrit.API(host=cfg.gerrit.host)

ja = jenkins.API(
    host=cfg.jenkins.host,
    user_id=cfg.jenkins.user_id,
    api_token=cfg.jenkins.api_token)

out = output.TextOutput(steps=5)

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
    out.failure("Build artifcats failed with %s", result)
    sys.exit(1)

out.success("Job completed successfully, congratulations!")
