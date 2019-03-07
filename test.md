# Test flow

Document the requests and expected responses during test flow.

## 1. Getting change refspec

Request:

    curl http://gerrit.ovirt.org./changes/?q=96774&o=CURRENT_REVISION

Response:

    [
      {
        "id": "vdsm~master~Ibd0cf4483b5bc92b81deb624c50f83ab0b73a6ba",
        "project": "vdsm",
        "branch": "master",
        "topic": "sos-read-only",
        "hashtags": [],
        "change_id": "Ibd0cf4483b5bc92b81deb624c50f83ab0b73a6ba",
        "subject": "sos: Use metadata_read_only\u003d1 for lvm commands",
        "status": "NEW",
        "created": "2019-01-10 02:13:32.418000000",
        "updated": "2019-03-05 00:25:44.178000000",
        "submit_type": "REBASE_IF_NECESSARY",
        "mergeable": true,
        "insertions": 14,
        "deletions": 9,
        "unresolved_comment_count": 1,
        "_number": 96774,
        "owner": {
          "_account_id": 1000466
        },
        "current_revision": "6872713066a4bc85b07a81d6bb860ac90215ac2a",
        "revisions": {
          "6872713066a4bc85b07a81d6bb860ac90215ac2a": {
            "kind": "TRIVIAL_REBASE",
            "_number": 7,
            "created": "2019-02-02 00:33:45.212000000",
            "uploader": {
              "_account_id": 1000466
            },
            "ref": "refs/changes/74/96774/7",
            "fetch": {
              "git": {
                "url": "git://gerrit.ovirt.org/vdsm",
                "ref": "refs/changes/74/96774/7"
              },
              "anonymous http": {
                "url": "https://gerrit.ovirt.org/vdsm",
                "ref": "refs/changes/74/96774/7"
              }
            }
          }
        }
      }
    ]

Extract the parameter for the build from the object:

STD_CI_REFSPEC = obj["revisions"][current_revision]["ref"]
STD_CI_CLONE_URL = obj["revisions"][current_revision]["fetch"]["url"]


## 2. Starting build artifacts job

Request:

    curl -i \
        --user username:API_TOKEN \
        -X POST \
        'https://jenkins.ovirt.org/job/standard-manual-runner/buildWithParameters?STD_CI_CLONE_URL=git://gerrit.ovirt.org/vdsm&STD_CI_REFSPEC=refs/changes/74/96774/7&STD_CI_STAGE=build-artifacts'

Response:

    HTTP/1.1 201 Created
    Date: Thu, 07 Mar 2019 00:00:38 GMT
    Server: Jetty(9.4.z-SNAPSHOT)
    X-Content-Type-Options: nosniff
    Location: https://jenkins.ovirt.org/queue/item/370116/
    Content-Length: 0
    Via: 1.1 jenkins.phx.ovirt.org-ssl
    Connection: close


## 3. Waiting until the build starts

Request:

    $ curl -g -i https://jenkins.ovirt.org/queue/item/370116/api/json?pretty=true'&tree=executable[url],blocked'

Response:

    {
      "_class" : "hudson.model.Queue$LeftItem",
      "blocked" : true,
    }

The task is blocked in the queue. We need to try again later.

    {
      "_class" : "hudson.model.Queue$LeftItem",
      "blocked" : false,
      "executable" : {
        "_class" : "org.jenkinsci.plugins.workflow.job.WorkflowRun",
        "url" : "http://jenkins.ovirt.org/job/standard-manual-runner/77/"
      }
    }

The task is building.


## 4. Waiting until the build finish

Request:

    $ curl -g -i https://jenkins.ovirt.org/job/standard-manual-runner/77/api/json?pretty=true'&tree=building,result'

Response:

    {
      "_class" : "org.jenkinsci.plugins.workflow.job.WorkflowRun",
      "building" : true,
      "result" : null
    }

The task is building. We need to try again later.

    {
      "_class" : "org.jenkinsci.plugins.workflow.job.WorkflowRun",
      "building" : false,
      "result" : "SUCCESS"
    }

The build is finished.


## 5. Starting OST build:

Request:

    $ curl -i --user username:API_TOKEN -X POST 'https://jenkins.ovirt.org/job/ovirt-system-tests_manual/buildWithParameters?SUITE_TYPE=basic&CUSTOM_REPOS=http://jenkins.ovirt.org/job/standard-manual-runner/77'

Response:

    HTTP/1.1 201 Created
    Date: Thu, 07 Mar 2019 00:21:03 GMT
    Server: Jetty(9.4.z-SNAPSHOT)
    X-Content-Type-Options: nosniff
    Location: https://jenkins.ovirt.org/queue/item/370143/
    Content-Length: 0
    Via: 1.1 jenkins.phx.ovirt.org-ssl
    Connection: close


## 6. Getting queue item info:

Request:

    $ curl -g 'https://jenkins.ovirt.org/queue/item/370143//api/json?pretty=true&tree=blocked,executable[url]'

Response:

    {
      "_class" : "hudson.model.Queue$LeftItem",
      "blocked" : false,
      "executable" : {
        "_class" : "hudson.model.FreeStyleBuild",
        "url" : "http://jenkins.ovirt.org/job/ovirt-system-tests_manual/4229/"
      }
    }


## 7. Watching the build

Request:

    $ curl -g 'http://jenkins.ovirt.org/job/ovirt-system-tests_manual/4229/api/json?pretty=true&tree=building,result'

Response:

    {
      "_class" : "hudson.model.FreeStyleBuild",
      "building" : true,
      "result" : null
    }

If the build fail:

    {
      "_class" : "hudson.model.FreeStyleBuild",
      "building" : false,
      "result" : "FAILURE"
    }

On success:

    {
      "_class" : "hudson.model.FreeStyleBuild",
      "building" : false,
      "result" : "SUCCESS"
    }
