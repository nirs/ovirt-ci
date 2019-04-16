import argparse
import logging
import sys

from . import config
from . import gerrit
from . import jenkins
from . import output

job_url = ''
queue_url = ''


def run():
    parser = argparse.ArgumentParser(
        description='A command line tool for working with Ovirt CI')

    parser.add_argument(
        '--debug',
        help="Show noisy debug logs",
        action="store_true")
    subparsers = parser.add_subparsers(title="commands")

    build_artifacts_parser = subparsers.add_parser(
        "build-artifacts",
        help="build artifacts for a change")
    build_artifacts_parser.set_defaults(command=build_artifacts)

    build_artifacts_parser.add_argument(
        'change',
        help='Gerrit change number')

    system_tests_parser = subparsers.add_parser(
        "system-tests",
        help="system-tests for a change")
    system_tests_parser.set_defaults(command=system_tests)

    system_tests_parser.add_argument(
        'change',
        help='Gerrit change number')

    system_tests_parser.add_argument(
        '--engine_version',
        default='master')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARNING,
        format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s")

    args.command(args)


def system_tests(args):
    global queue_url
    global job_url
    cfg = config.load()

    suite_type = "basic"

    ja = jenkins.API(
        host=cfg.jenkins.host,
        user_id=cfg.jenkins.user_id,
        api_token=cfg.jenkins.api_token)

    build_artifacts(args, (cfg, ja))

    out = output.TextOutput(steps=8)

    out.step("Starting oVirt system tests job")
    out.info(("suite", suite_type), ("repo", job_url))
    queue_url = ja.build(
        "ovirt-system-tests_manual",
        parameters={
            "CUSTOM_REPOS": job_url,
            "ENGINE_VERSION": args.engine_version,
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


def build_artifacts(args, (cfg, ja)=None):
    global queue_url
    global job_url

    if not cfg:
        cfg = config.load()

        ja = jenkins.API(
            host=cfg.jenkins.host,
            user_id=cfg.jenkins.user_id,
            api_token=cfg.jenkins.api_token)

    ga = gerrit.API(host=cfg.gerrit.host)

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
