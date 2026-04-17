# FounderAssignRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contingency_fee_percent** | **float** |  | [optional]
**reason** | **str** |  | [optional]

## Example

```python
from xr7_sdk.models.founder_assign_request import FounderAssignRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FounderAssignRequest from a JSON string
founder_assign_request_instance = FounderAssignRequest.from_json(json)
# print the JSON string representation of the object
print(FounderAssignRequest.to_json())

# convert the object into a dict
founder_assign_request_dict = founder_assign_request_instance.to_dict()
# create an instance of FounderAssignRequest from a dict
founder_assign_request_from_dict = FounderAssignRequest.from_dict(founder_assign_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
