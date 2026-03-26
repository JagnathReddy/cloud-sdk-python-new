# Document Management Service draft user guide

This module provides a Python client for the SAP Document Management Service (DMS). It covers both the **Admin API** (repository and configuration management) and the **CMIS Browser Binding API** (folders, documents, versioning, ACLs).

## Installation

```bash

# Using pip
pip install sap-cloud-sdk
```

See further information about installation in the [main documentation](/README.md#installation).

## Import

```python
from sap_cloud_sdk.dms import create_client
from sap_cloud_sdk.dms.model import (
    InternalRepoRequest, UpdateRepoRequest, Repository,
    CreateConfigRequest, UpdateConfigRequest, RepositoryConfig, ConfigName,
    UserClaim, Ace, Acl, Folder, Document, CmisObject, ChildrenPage,
)
from sap_cloud_sdk.dms.exceptions import (
    DMSError, DMSObjectNotFoundException, DMSPermissionDeniedException,
    DMSInvalidArgumentException, DMSConnectionError, DMSRuntimeException,
)
```

---

## Getting Started

Use `create_client()` to get a client with automatic configuration detection:

```python
from sap_cloud_sdk.dms import create_client

# Load credentials from mounted secrets or environment variables
client = create_client(instance="my-instance")
```

You can also provide credentials directly:

```python
from sap_cloud_sdk.dms import create_client
from sap_cloud_sdk.dms.model import DMSCredentials

creds = DMSCredentials(
    instance_name="my-instance",
    uri="https://api-sdm-di.cfapps.eu10.hana.ondemand.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://your-subdomain.authentication.eu10.hana.ondemand.com/oauth/token",
    identityzone="your-subdomain",
)

client = create_client(dms_cred=creds)
```

> **`instance` refers to the instance name defined in your Cloud descriptor.**
>
> This name determines which set of credentials or mounted secrets to resolve from the environment.

---

## User Identity (UserClaim)

Many DMS operations accept an optional `user_claim` parameter to impersonate a user when the SDK authenticates via `client_credentials` grant. This forwards `X-EcmUserEnc` and `X-EcmAddPrincipals` headers to the service.

```python
from sap_cloud_sdk.dms.model import UserClaim

claim = UserClaim(
    x_ecm_user_enc="john.doe@example.com",
    x_ecm_add_principals=["~GroupA", "~GroupB", "another.user@example.com"],
)

# Pass to any API call
repos = client.get_all_repositories(user_claim=claim)
```

Groups are prefixed with `~`. Omit the `user_claim` parameter to use the service identity.

---

## Admin API — Repository Management

### Onboard a Repository

```python
from sap_cloud_sdk.dms.model import InternalRepoRequest

request = InternalRepoRequest(
    displayName="My Repository",
    description="Main document store",
    isVersionEnabled=True,
    isVirusScanEnabled=True,
)

repo = client.onboard_repository(request)
print(f"Created: {repo.name} (id={repo.id})")
```

### List All Repositories

```python
repos = client.get_all_repositories()

for repo in repos:
    print(f"{repo.name} — {repo.repository_type} — id={repo.id}")
    print(f"  CMIS repo ID: {repo.cmis_repository_id}")
    print(f"  Versioning: {repo.get_param('isVersionEnabled')}")
```

### Get a Single Repository

```python
repo = client.get_repository("repository-uuid")
print(f"{repo.name}: {repo.repository_category}")
```

### Update a Repository

```python
from sap_cloud_sdk.dms.model import UpdateRepoRequest

request = UpdateRepoRequest(
    description="Updated description",
    isVirusScanEnabled=False,
)

repo = client.update_repository("repository-uuid", request)
```

### Delete a Repository

```python
client.delete_repository("repository-uuid")
```

---

## Admin API — Configuration Management

### Create a Configuration

```python
from sap_cloud_sdk.dms.model import CreateConfigRequest, ConfigName

request = CreateConfigRequest(
    config_name=ConfigName.BLOCKED_FILE_EXTENSIONS,
    config_value="bat,dmg,exe",
)

config = client.create_config(request)
print(f"Config: {config.config_name} = {config.config_value}")
```

### Get All Configurations

```python
configs = client.get_configs()

for cfg in configs:
    print(f"{cfg.config_name} = {cfg.config_value} (id={cfg.id})")
```

### Update a Configuration

```python
from sap_cloud_sdk.dms.model import UpdateConfigRequest

request = UpdateConfigRequest(
    id="config-uuid",
    config_name=ConfigName.BLOCKED_FILE_EXTENSIONS,
    config_value="bat,dmg,exe,msi",
)

config = client.update_config("config-uuid", request)
```

### Delete a Configuration

```python
client.delete_config("config-uuid")
```

---

## CMIS API — Folder Operations

All CMIS operations require a `repository_id` (the CMIS repository ID from `repo.cmis_repository_id`) and use the CMIS Browser Binding protocol under the hood.

### Create a Folder

```python
folder = client.create_folder(
    repository_id="cmis-repo-id",
    parent_folder_id="root-folder-object-id",
    folder_name="My Folder",
    description="Optional description",
)

print(f"Created folder: {folder.name} (objectId={folder.object_id})")
```

### Create a Folder with ACLs

```python
from sap_cloud_sdk.dms.model import Ace

folder = client.create_folder(
    repository_id="cmis-repo-id",
    parent_folder_id="root-folder-object-id",
    folder_name="Secured Folder",
    add_aces=[
        Ace(principal_id="user@example.com", permissions=["cmis:read", "cmis:write"]),
    ],
)
```

---

## CMIS API — Document Operations

### Create a Document

```python
import io

# From in-memory bytes
content = io.BytesIO(b"Hello, World!")
doc = client.create_document(
    repository_id="cmis-repo-id",
    parent_folder_id="parent-folder-id",
    document_name="hello.txt",
    file=content,
    mime_type="text/plain",
)

print(f"Created: {doc.name} ({doc.content_stream_length} bytes)")
print(f"Version: {doc.version_label}")
```

### Upload a File from Disk

```python
with open("/path/to/report.pdf", "rb") as f:
    doc = client.create_document(
        repository_id="cmis-repo-id",
        parent_folder_id="parent-folder-id",
        document_name="report.pdf",
        file=f,
        mime_type="application/pdf",
        description="Q4 financial report",
    )
```

### Download Document Content

```python
response = client.get_content(
    repository_id="cmis-repo-id",
    document_id="document-object-id",
    download="attachment",
)

try:
    with open("downloaded.pdf", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
finally:
    response.close()
```

Optional parameters:
- `stream_id` — download a specific rendition (e.g. `"sap:zipRendition"`)
- `filename` — override the filename in the response header

---

## CMIS API — Versioning

Versioning requires a version-enabled repository.

### Check Out a Document

Creates a Private Working Copy (PWC):

```python
pwc = client.check_out(
    repository_id="cmis-repo-id",
    document_id="document-object-id",
)

print(f"PWC objectId: {pwc.object_id}")
print(f"Is PWC: {pwc.is_private_working_copy}")
```

### Check In a Document

Creates a new version from the PWC:

```python
import io

new_content = io.BytesIO(b"Updated content for v2")

doc = client.check_in(
    repository_id="cmis-repo-id",
    document_id=pwc.object_id,      # the PWC objectId
    major=True,
    file=new_content,
    file_name="hello.txt",
    mime_type="text/plain",
    checkin_comment="Version 2.0 — updated content",
)

print(f"New version: {doc.version_label}")
print(f"Is latest: {doc.is_latest_version}")
```

### Cancel Check Out

Discards the PWC without creating a new version:

```python
client.cancel_check_out(
    repository_id="cmis-repo-id",
    document_id=pwc.object_id,
)
```

---

## CMIS API — Access Control Lists (ACL)

### Get the Current ACL

```python
acl = client.apply_acl(
    repository_id="cmis-repo-id",
    object_id="document-or-folder-id",
)

for ace in acl.aces:
    print(f"{ace.principal_id}: {ace.permissions} (direct={ace.is_direct})")
```

### Add ACE Entries

```python
from sap_cloud_sdk.dms.model import Ace

acl = client.apply_acl(
    repository_id="cmis-repo-id",
    object_id="document-or-folder-id",
    add_aces=[
        Ace(principal_id="user@example.com", permissions=["cmis:read"]),
        Ace(principal_id="admin@example.com", permissions=["cmis:all"]),
    ],
)
```

### Remove ACE Entries

```python
acl = client.apply_acl(
    repository_id="cmis-repo-id",
    object_id="document-or-folder-id",
    remove_aces=[
        Ace(principal_id="user@example.com", permissions=["cmis:read"]),
    ],
)
```

### ACL Propagation

Control whether ACL changes propagate to children:

```python
acl = client.apply_acl(
    repository_id="cmis-repo-id",
    object_id="folder-id",
    add_aces=[Ace(principal_id="team@example.com", permissions=["cmis:read"])],
    acl_propagation="propagate",  # "propagate" | "objectonly" | "repositorydetermined"
)
```

---

## CMIS API — Reading Objects

### Get Object by ID

Returns `Folder`, `Document`, or `CmisObject` depending on the base type:

```python
obj = client.get_object(
    repository_id="cmis-repo-id",
    object_id="some-object-id",
    include_acl=True,
)

print(f"Type: {type(obj).__name__}")
print(f"Name: {obj.name}")
print(f"Modified: {obj.last_modification_date}")

if isinstance(obj, Document):
    print(f"MIME: {obj.content_stream_mime_type}")
    print(f"Size: {obj.content_stream_length}")
    print(f"Version: {obj.version_label}")
```

### Update Properties

```python
updated = client.update_properties(
    repository_id="cmis-repo-id",
    object_id="some-object-id",
    properties={
        "cmis:name": "Renamed Document.pdf",
        "cmis:description": "Updated description",
    },
)

print(f"New name: {updated.name}")
```

Use `change_token` for optimistic concurrency control:

```python
updated = client.update_properties(
    repository_id="cmis-repo-id",
    object_id="some-object-id",
    properties={"cmis:name": "New Name"},
    change_token="current-change-token-value",
)
```

### List Children (Pagination)

```python
page = client.get_children(
    repository_id="cmis-repo-id",
    folder_id="parent-folder-id",
    max_items=50,
    skip_count=0,
    order_by="cmis:creationDate ASC",
)

print(f"Items: {len(page.objects)}, hasMore: {page.has_more_items}, total: {page.num_items}")

for obj in page.objects:
    kind = "Folder" if isinstance(obj, Folder) else "Document"
    print(f"  [{kind}] {obj.name} — {obj.object_id}")
```

Paginate through all children:

```python
skip = 0
page_size = 100

while True:
    page = client.get_children(
        repository_id="cmis-repo-id",
        folder_id="parent-folder-id",
        max_items=page_size,
        skip_count=skip,
    )

    for obj in page.objects:
        print(obj.name)

    if not page.has_more_items:
        break
    skip += page_size
```

---
