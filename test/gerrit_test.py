from oci import gerrit

def test_build_info():
    ga = gerrit.API("gerrit.ovirt.org")
    res = ga.build_info("96774")

    assert res == {
        "ref": "refs/changes/74/96774/7",
        "url": "git://gerrit.ovirt.org/vdsm",
    }
