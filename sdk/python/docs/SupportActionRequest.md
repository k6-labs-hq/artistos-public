# SupportActionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | **str** | one_of_safe_actions |
**payload** | **Dict[str, object]** |  | [optional]

## Example

```python
from xr7_sdk.models.support_action_request import SupportActionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SupportActionRequest from a JSON string
support_action_request_instance = SupportActionRequest.from_json(json)
# print the JSON string representation of the object
print(SupportActionRequest.to_json())

# convert the object into a dict
support_action_request_dict = support_action_request_instance.to_dict()
# create an instance of SupportActionRequest from a dict
support_action_request_from_dict = SupportActionRequest.from_dict(support_action_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
