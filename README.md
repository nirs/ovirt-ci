# oci

[![Build Status](https://travis-ci.org/nirs/oci.svg?branch=master)](https://travis-ci.org/nirs/oci)

Command line tool for working with oVirt CI.

## Setup

Visit https://jenkins.ovirt.org/user/username/configure
and create an API Token.

Keep your Jenkins user id and API Token in the configuration file at:

    ~/.config/oci.conf

Here is an example configuration file:

    [jenkins]
    user_id = johnd
    api_token = 3e8cd699a2564d9ba2855831bf4cb5eb


## Usage

Running oVirt system tests with a change:

    $ oci test 54321

This commands builds artifacts with the patch above, and run oVirt
system tests job with the built artifacts. When the test run is
completed, add a comment about the run to the patch.


## Running the tests

    $ tox
