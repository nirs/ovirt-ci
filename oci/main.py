import argparse
import logging
import sys
import daemon

from . import config
from . import gerrit
from . import jenkins
from . import output


def run():
    parser = argparse.ArgumentParser(
        description='A command line tool for working with Ovirt CI')

    parser.add_argument(
        '--debug',
        help="Show noisy debug logs",
        action="store_true")

    parser.add_argument(
        '--daemon',
        help="Run as daemon and redirect output to /var/tmp/oci_{command}_{change id}.log",
        action="store_true")
    subparsers = parser.add_subparsers(title="commands")

    build_artifacts_parser = subparsers.add_parser(
        "build-artifacts",
        help="build artifacts for a change")
    build_artifacts_parser.set_defaults(command=invoke_build_artifacts)

    build_artifacts_parser.add_argument(
        'change',
        help='Gerrit change number')

    system_tests_parser = subparsers.add_parser(
        "system-tests",
        help="run system tests for a change")
    system_tests_parser.set_defaults(command=invoke_system_tests)

    system_tests_parser.add_argument(
        'change',
        help='Gerrit change number')

    system_tests_parser.add_argument(
        '--engine-version',
        help='Supported versions can be found at '
             'https://jenkins.ovirt.org/job/ovirt-system-tests_manual/build '
             'under "ENGINE_VERSION"',
        default='master')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARNING,
        format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s")

    args.command(args)

def invoke_system_tests(args):
    if args.daemon:
        with open("/var/tmp/oci_system_tests_{}_.log".format(args.change), 'w') as f:
            with daemon.DaemonContext(stdout=f,stderr=f):
                system_tests(args)
    else:
        system_tests(args)

def system_tests(args):
    cfg = config.load()

    suite_type = "basic"

    ga = gerrit.API(host=cfg.gerrit.host)

    ja = jenkins.API(
        host=cfg.jenkins.host,
        user_id=cfg.jenkins.user_id,
        api_token=cfg.jenkins.api_token)

    out = output.TextOutput(steps=8)

    # TODO: the build-artifacts flow was copied from build-artifacts.py. Find a
    # way to reuse the code instead of copying it.

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
        out.failure("Build artifacts %s failed", job_url)
        sys.exit(1)

    out.step("Starting oVirt system tests job")
    out.info(("suite", suite_type), ("repo", job_url))
    queue_url = ja.system_tests(
        custom_repos=job_url,
        engine_version=args.engine_version,
        suite_type=suite_type)

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

def invoke_build_artifacts(args):
    if args.daemon:
        with open("/var/tmp/oci_build_artifcats_{}_.log".format(args.change), 'w') as f:
            with daemon.DaemonContext(stdout=f,stderr=f):
                build_artifacts(args)
    else:
        build_artifacts(args)

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
