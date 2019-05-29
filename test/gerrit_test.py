from ovirt_ci import gerrit


def test_build_info():
    ga = gerrit.API("gerrit.ovirt.org")
    res = ga.build_info("98719")

    assert res == {
        "project": "vdsm",
        "branch": "ovirt-4.3",
        "patchset": 2,
        "ref": "refs/changes/19/98719/2",
        "url": "git://gerrit.ovirt.org/vdsm",
    }
