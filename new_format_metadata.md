### Examples of metadata state at various stages of archiving and retrieving

---
#### Sequence of status updates for `archival_status` key during archiving process:

`processing_metadata` -> `validating_archived_path` -> `ready_for_queue` -> `submitting` -> `queued` -> `processing` -> `completed`

---
#### Metadata when ready for mongoDB
Example of metadata when ready for insertion into mongoDB.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "when_ready_for_queue": null,
    "when_archival_queued": null,
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_count": 0,
    "archival_status": "processing_metadata",
    "user_metadata": {},
}
```

Back to [archive][metadata_link]

---
#### Metadata after initially inserted
Example of metadata after initially inserted into mongoDB.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "when_ready_for_queue": null,
    "when_archival_queued": null,
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_count": 0,
    "archival_status": "validating_archived_path",
    "user_metadata": {},
}
```

Back to [archive][metadata_link]


---
#### Metadata when ready for submitting to pbs
Example of metadata right before `submit_to_pbs()`.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": null,
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_count": 0,
    "archival_status": "ready_for_queue",
    "user_metadata": {},
    "job_id": "8638.ctarchive.jax.org",
}
```

Back to [archive][metadata_link]


---
#### Metadata after submitted to pbs (queued)
Example of metadata right after `submit_to_pbs()`.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_count": 0,
    "archival_status": "queued",
    "user_metadata": {},
    "job_id": "8638.ctarchive.jax.org",
}
```

Back to [archive][metadata_link]

---
#### Metadata archive processing
Example of metadata state when `/archive_processing` updates metadata.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
    "when_archival_completed": null,
    "failed_count": 0,
    "archival_status": "processing",
    "user_metadata": {},
    "job_id": "8638.ctarchive.jax.org",
}
```

Back to [`/archive_processing`][5]

---
#### Metadata archive pre-completed
Example of metadata state when `/archive_success` updates metadata.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
    "when_archival_completed": "2020-01-01 03:01:59 EDT-0400",
    "failed_count": 0,
    "archival_status": "completed",
    "archived_size": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-01-01",
    "source_size": {
        "$numberInt": "797725536"
    },
    "user_metadata": {},
    "job_id": "8638.ctarchive.jax.org",
}
```

Back to [`/archive_success`][6]

---

#### Metadata archive completed
Example of metadata when archiving is completed.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "archival_status": "completed",
    "archived_size": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-01-01",
    "source_size": {
        "$numberInt": "797725536"
    },
    "user_metadata": {},
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    }
}
```

Back to [`/archive_success`][6]

---

#### Metadata archive failed
Example of metadata state when `/archive_failed` updates metadata. Note that metadata state can look different from example below depending on what stage of archiving process the failure happens.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
    "when_archival_failed": "2019-12-31 22:46:08 EDT-0400",
    "when_archival_completed": null,
    "failed_count": 0,
    "archival_status": "failed",
    "user_metadata": {},
    "job_id": "8638.ctarchive.jax.org",
}
```

Back to [`/archive_failed`][4]

---

#### Metadata retrieve request ready
Example of metadata when request ready for submission to pbs.
```
{
	"current_user": {
		"fname": "Research",
		"lname": "IT",
		"username": "rit",
		"email": "rit@jax.org"
	},
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "archival_status": "completed",
    "submit_progress": [],
    "archived_size": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-01-01",
    "source_size": {
        "$numberInt": "797725536"
    },
    "user_metadata":{},
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    },
}
```

Back to [`/retrieve`][2]

---


#### Metadata retrieve request submitted
Example of metadata when request submitted to pbs (queued).
```
{
	"current_user": {
		"fname": "Research",
		"lname": "IT",
		"username": "rit",
		"email": "rit@jax.org"
	},
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "archival_status": "completed",
    "submit_progress": [],
    "archived_size": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-01-01",
    "source_size": {
        "$numberInt": "797725536"
    },
    "user_metadata":{},
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    },
    "retrievals": [{
    "job_id": "8649.ctarchive.jax.org",
    "retrieval_status": "queued",
    "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
    "when_retrieval_started": null,
    "when_retrieval_completed": null
	}]
}
```

Back to [`/retrieve`][2]

---

#### Metadata retrieve processing
Example of metadata after retrieve job begins processing.
```
{
	"current_user": {
		"fname": "Research",
		"lname": "IT",
		"username": "rit",
		"email": "rit@jax.org"
	},
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "archival_status": "completed",
    "submit_progress": [],
    "archived_size": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-01-01",
    "source_size": {
        "$numberInt": "797725536"
    },
    "user_metadata":{},
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    },
    "retrievals": [{
    "job_id": "8649.ctarchive.jax.org",
    "retrieval_status": "processing",
    "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
    "when_retrieval_started": "2020-01-02 07:36:25 EDT-0400",
    "when_retrieval_completed": null
	}]
}
```

Back to [`/retrieve_processing`][8]

---

#### Metadata retrieve success
Example of metadata after retrieve job completes.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "archival_status": "completed",
    "submit_progress": [],
    "archived_size": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-01-01",
    "source_size": {
        "$numberInt": "797725536"
    },
    "user_metadata":{},
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    },
    "retrievals": [{
    "job_id": "8649.ctarchive.jax.org",
    "retrieval_status": "completed",
    "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
    "when_retrieval_started": "2020-01-02 07:36:25 EDT-0400",
    "when_retrieval_completed": "2020-01-02 13:42:53 EDT-0400",
    "username": "rit"
	}]
}
```

Back to [`/retrieve_success`][9]

---

#### Metadata retrieve failed
Example of metadata when retrieval job fails.
```
{
    "manager_user_id": "pi",
    "user_id": "postdoc",
    "project_name": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archived_path": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "source_path": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "archival_status": "completed",
    "submit_progress": [],
    "archived_size": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-01-01",
    "source_size": {
        "$numberInt": "797725536"
    },
    "user_metadata":{},
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_ready_for_queue": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    },
    "retrievals": [{
    "job_id": "8649.ctarchive.jax.org",
    "retrieval_status": "failed",
    "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
    "when_retrieval_started": "2020-03-30 12:32:15 EDT-0400",
    "when_retrieval_failed": "2020-03-30 12:39:27 EDT-0400",
    "when_retrieval_completed": null,
    "username": "rit"
  }]
}
```

Back to [`/retrieve_failed`][7]

---


[1]: README.md#archive
[2]: README.md#retrieve
[3]: README.md#collection-endpoints
[4]: README.md#archive_failed
[5]: README.md#archive_processing
[6]: README.md#archive_success
[7]: README.md#retrieve_failed
[8]: README.md#retrieve_processing
[9]: README.md#retrieve_success
[10]: README.md#get_documents
[11]: README.md#get_document_by_objectid
[12]: README.md#get_last_document
[frontend]: https://github.com/TheJacksonLaboratory/archive-frontend
[endpoints]: README.md#endpoints
[metadata_link]: README.md#metadata
[example_metadata]: README.md#example-metadata
