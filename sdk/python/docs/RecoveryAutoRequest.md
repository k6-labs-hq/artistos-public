# RecoveryAutoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**include_rights_registration** | **bool** |  | [optional] [default to True]

## Example

```python
from xr7_sdk.models.recovery_auto_request import RecoveryAutoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RecoveryAutoRequest from a JSON string
recovery_auto_request_instance = RecoveryAutoRequest.from_json(json)
# print the JSON string representation of the object
print(RecoveryAutoRequest.to_json())

# convert the object into a dict
recovery_auto_request_dict = recovery_auto_request_instance.to_dict()
# create an instance of RecoveryAutoRequest from a dict
recovery_auto_request_from_dict = RecoveryAutoRequest.from_dict(recovery_auto_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


