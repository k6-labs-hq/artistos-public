# SyncJobSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**integration** | **str** |  | 
**status** | **str** |  | 
**attempts** | **int** |  | 
**max_attempts** | **int** |  | 
**last_error** | **str** |  | 
**payload_json** | **str** |  | 
**result_json** | **str** |  | 
**queue_backend** | **str** |  | 
**last_task_id** | **str** |  | 
**enqueued_at** | **datetime** |  | 
**next_run_at** | **datetime** |  | 
**started_at** | **datetime** |  | 
**completed_at** | **datetime** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.sync_job_schema import SyncJobSchema

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of SyncJobSchema from a JSON string
sync_job_schema_instance = SyncJobSchema.from_json(json)
# print the JSON string representation of the object
print(SyncJobSchema.to_json())

# convert the object into a dict
sync_job_schema_dict = sync_job_schema_instance.to_dict()
# create an instance of SyncJobSchema from a dict
sync_job_schema_from_dict = SyncJobSchema.from_dict(sync_job_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


