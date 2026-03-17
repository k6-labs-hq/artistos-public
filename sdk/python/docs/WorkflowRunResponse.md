# WorkflowRunResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  | 
**run_id** | **str** |  | 
**status** | **str** |  | 
**status_url** | **str** |  | 
**branding** | **Dict[str, object]** |  | [optional] 

## Example

```python
from xr7_sdk.models.workflow_run_response import WorkflowRunResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowRunResponse from a JSON string
workflow_run_response_instance = WorkflowRunResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowRunResponse.to_json())

# convert the object into a dict
workflow_run_response_dict = workflow_run_response_instance.to_dict()
# create an instance of WorkflowRunResponse from a dict
workflow_run_response_from_dict = WorkflowRunResponse.from_dict(workflow_run_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


