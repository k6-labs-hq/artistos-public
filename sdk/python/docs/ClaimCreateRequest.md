# ClaimCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anomaly_id** | **str** |  | 
**claim_type** | **str** |  | [optional] [default to 'RECOVERY']

## Example

```python
from xr7_sdk.models.claim_create_request import ClaimCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ClaimCreateRequest from a JSON string
claim_create_request_instance = ClaimCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ClaimCreateRequest.to_json())

# convert the object into a dict
claim_create_request_dict = claim_create_request_instance.to_dict()
# create an instance of ClaimCreateRequest from a dict
claim_create_request_from_dict = ClaimCreateRequest.from_dict(claim_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


