# RecoverySubmitResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**claim_id** | **str** |  |
**status** | **str** |  |
**queued** | **bool** |  |
**task_id** | **str** |  | [optional]

## Example

```python
from xr7_sdk.models.recovery_submit_response import RecoverySubmitResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RecoverySubmitResponse from a JSON string
recovery_submit_response_instance = RecoverySubmitResponse.from_json(json)
# print the JSON string representation of the object
print(RecoverySubmitResponse.to_json())

# convert the object into a dict
recovery_submit_response_dict = recovery_submit_response_instance.to_dict()
# create an instance of RecoverySubmitResponse from a dict
recovery_submit_response_from_dict = RecoverySubmitResponse.from_dict(recovery_submit_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
