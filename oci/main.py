import argparse
import sys

from . import config
from . import gerrit
from . import jenkins
from . import output


def run():
    parser = argparse.ArgumentParser(
        description='A command line tool for working with Ovirt CI')

    parser.add_argument(
        '--verbose',
        help="increase output verbosity",
        action="store_true")
    subparsers = parser.add_subparsers(title="commands")

    build_artifacts_parser = subparsers.add_parser(
        "build-artifacts",
        help="build artifacts for a change")
    build_artifacts_parser.set_defaults(command=build_artifacts)

    build_artifacts_parser.add_argument(
        'change',
        help='Gerrit change number')

    args = parser.parse_args()

    args.command(args)


def build_artifacts(args):
    cfg = config.load()

    ga = gerrit.API(host=cfg.gerrit.host)

    ja = jenkins.API(
        host=cfg.jenkins.host,
        user_id=cfg.jenkins.user_id,
        api_token=cfg.jenkins.api_token)

    out = output.TextOutput(steps=5)

    out.step("Getting build info for change %s", args.change)
    info = ga.build_info(args.change)

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
