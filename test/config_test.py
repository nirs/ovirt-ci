from contextlib import contextmanager
import pytest

from oci.oci import config


@contextmanager
def write_config_file(tmpdir, cfg_data):
    cfg_file = tmpdir.join("oci.conf")
    cfg_file.write(cfg_data)
    try:
        yield cfg_file
    finally:
        pass


def test_load_minimal(tmpdir):
    cfg_data = """[jenkins]
user_id = fred
api_token = 12345
"""
    with write_config_file(tmpdir, cfg_data) as cfg_file:
        cfg = config.load(str(cfg_file))

    assert cfg.jenkins.user_name == 'fred'
    assert cfg.jenkins.api_token == '12345'
    assert cfg.jenkins.host == 'jenkins.ovirt.org'
    assert cfg.gerrit.host == 'gerrit.ovirt.org'


def test_missing_required_options(tmpdir):
    cfg_data = """[jenkins]
user_id = fred
"""
    with write_config_file(tmpdir, cfg_data) as cfg_file:
        with pytest.raises(config.Error) as err:
            config.load(str(cfg_file))
            assert err == config.Error


def test_load_custom_config_that_has_(tmpdir):
    cfg_data = """[jenkins]
user_id = fred
api_token = 12345
host = dummy.jenkins.org
[gerrit]
host = dummy.gerrit.org
"""
    with write_config_file(tmpdir, cfg_data) as cfg_file:
        cfg = config.load(str(cfg_file))

    assert cfg.jenkins.host == 'dummy.jenkins.org'
    assert cfg.gerrit.host == 'dummy.gerrit.org'
