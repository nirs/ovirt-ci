from collections import namedtuple
import ConfigParser
import os

gerrit_default_host = 'gerrit.ovirt.org'
jenkins_default_host = 'jenkins.ovirt.org'


def load():
    config_dir = os.path.join(os.path.expanduser('~'), '.config/oci.conf')
    config = ConfigParser.RawConfigParser(allow_no_value=True)

    with open(config_dir, 'r') as config_file:
        config.readfp(config_file)

        # set default Jenkins host if not present
        jenkins_host = jenkins_default_host
        if config.has_option('jenkins', 'host'):
            jenkins_host = config.get('jenkins', 'host')

        # set default Gerrit host if not present
        gerrit_host = jenkins_default_host
        if config.has_option('gerrit', 'host'):
            gerrit_host = config.get('gerrit', 'host')

        try:
            token = config.get('jenkins', 'api_token')
            user = config.get('jenkins', 'user_id')
        except ConfigParser.NoOptionError as e:
            raise Exception(
                'A setting in the config file is missing: ', e)

    Jenkins = namedtuple('jenkins', 'host, user_name, api_token')
    Gerrit = namedtuple('gerrit', 'host')
    Config = namedtuple('config', 'jenkins, gerrit')

    result = Config(
        jenkins=Jenkins(
            host=jenkins_host,
            user_name=user,
            api_token=token),
        gerrit=Gerrit(
            host=gerrit_host
        ))

    return result
