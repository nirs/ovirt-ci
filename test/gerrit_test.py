from oci import gerrit


def test_build_info():
    ga = gerrit.API("gerrit.ovirt.org")
    res = ga.build_info("98719")

    assert res == {
        "ref": "refs/changes/19/98719/2",
        "url": "git://gerrit.ovirt.org/vdsm",
    }
