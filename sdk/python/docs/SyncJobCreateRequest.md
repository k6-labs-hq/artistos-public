# SyncJobCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration** | **str** |  | 
**max_attempts** | **int** |  | [optional] [default to 3]
**payload** | **Dict[str, object]** |  | [optional] 
**run_async** | **bool** |  | [optional] [default to True]
**queue_backend** | **str** |  | [optional] [default to 'background']

## Example

```python
from xr7_sdk.models.sync_job_create_request import SyncJobCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SyncJobCreateRequest from a JSON string
sync_job_create_request_instance = SyncJobCreateRequest.from_json(json)
# print the JSON string representation of the object
print(SyncJobCreateRequest.to_json())

# convert the object into a dict
sync_job_create_request_dict = sync_job_create_request_instance.to_dict()
# create an instance of SyncJobCreateRequest from a dict
sync_job_create_request_from_dict = SyncJobCreateRequest.from_dict(sync_job_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


