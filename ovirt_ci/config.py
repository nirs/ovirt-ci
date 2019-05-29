from collections import namedtuple
import os
from six.moves import configparser

DEFAULT_CONFIG = {
    ('jenkins', 'host', 'jenkins.ovirt.org'),
    ('gerrit', 'host', 'gerrit.ovirt.org')}

Jenkins = namedtuple('jenkins', 'host, user_id, api_token')
Gerrit = namedtuple('gerrit', 'host')
Config = namedtuple('config', 'jenkins, gerrit')


class Error(Exception):
    pass


def config_parser():
    cfg = configparser.RawConfigParser()

    # Setup default configuration
    for (section, key, value) in DEFAULT_CONFIG:
        cfg.add_section(section)
        cfg.set(section, key, value)

    return cfg


def load(path=os.path.expanduser("/home/blevin/.config/ovirt_ci.conf")):
    cfg = config_parser()

    cfg.read(path)
    try:
        return Config(
            jenkins=Jenkins(
                host=cfg.get('jenkins', 'host'),
                user_id=cfg.get('jenkins', 'user_id'),
                api_token=cfg.get('jenkins', 'api_token')),
            gerrit=Gerrit(
                host=cfg.get('gerrit', 'host')
            ))
    except configparser.NoOptionError as err:
        raise Error(
            "Option {!r} in section {!r} is required"
            .format(err.option, err.section))
