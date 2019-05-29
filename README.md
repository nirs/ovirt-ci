# Ovirt-CI

[![Build Status](https://travis-ci.org/nirs/oci.svg?branch=master)](https://travis-ci.org/nirs/oci)

Command line tool for working with oVirt CI.


## Installation

On Fedora 28 or later:

    sudo dnf install python2-gobject

If the distribution package is too old, you can install from pip as a
user:

    pip install -r requirements.txt --user


## Setup

Visit https://jenkins.ovirt.org/user/username/configure
and create an API Token.

Keep your Jenkins user id and API Token in the configuration file at:

    ~/.config/ovirt-ci.conf

Here is an example configuration file:

    [jenkins]
    user_id = johnd
    api_token = 3e8cd699a2564d9ba2855831bf4cb5eb


## Usage

Building artifacts for a change:

    $ ./ovirt-ci build-artifacts 54321

This command will invoke the build-artifacts stage for the project. You
can use the job URL printed by the command to run oVirt system tests
manually.

Running oVirt system tests with a change:

    $ ovirt-ci system-tests 54321

This commands builds artifacts with the patch above, and run oVirt
system tests job with the built artifacts. When the test run is
completed, add a comment about the run to the patch.


## Contributing

PRs are welcome!

First instal tox.

On Fedora:

    $ sudo dnf install python2-tox

If the distribution tox is too old, you can install using:

    $ pip install tox --user.

To run the tests locally, use:

    $ tox
