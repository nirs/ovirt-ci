import pytest

from oci import config


def test_load_minimal(tmpdir):
    cfg_data = """[jenkins]
user_id = fred
api_token = 12345
"""
    cfg_file = tmpdir.join("oci.conf")
    cfg_file.write(cfg_data)
    cfg = config.load(str(cfg_file))

    assert cfg.jenkins.user_id == 'fred'
    assert cfg.jenkins.api_token == '12345'
    assert cfg.jenkins.host == 'jenkins.ovirt.org'
    assert cfg.gerrit.host == 'gerrit.ovirt.org'


def test_missing_required_options(tmpdir):
    cfg_data = """[jenkins]
user_id = fred
"""
    cfg_file = tmpdir.join("oci.conf")
    cfg_file.write(cfg_data)
    with pytest.raises(config.Error):
        config.load(str(cfg_file))


def test_override_default_host(tmpdir):
    cfg_data = """[jenkins]
user_id = fred
api_token = 12345
host = dummy.jenkins.org
[gerrit]
host = dummy.gerrit.org
"""
    cfg_file = tmpdir.join("oci.conf")
    cfg_file.write(cfg_data)
    cfg = config.load(str(cfg_file))

    assert cfg.jenkins.host == 'dummy.jenkins.org'
    assert cfg.gerrit.host == 'dummy.gerrit.org'
