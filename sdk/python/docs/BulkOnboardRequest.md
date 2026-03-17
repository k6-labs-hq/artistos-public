# BulkOnboardRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artists** | **List[Dict[str, object]]** |  | 

## Example

```python
from xr7_sdk.models.bulk_onboard_request import BulkOnboardRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkOnboardRequest from a JSON string
bulk_onboard_request_instance = BulkOnboardRequest.from_json(json)
# print the JSON string representation of the object
print(BulkOnboardRequest.to_json())

# convert the object into a dict
bulk_onboard_request_dict = bulk_onboard_request_instance.to_dict()
# create an instance of BulkOnboardRequest from a dict
bulk_onboard_request_from_dict = BulkOnboardRequest.from_dict(bulk_onboard_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


