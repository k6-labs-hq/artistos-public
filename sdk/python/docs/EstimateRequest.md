# EstimateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**estimate_token** | **str** |  |
**career_stage** | **str** |  | [optional] [default to 'DEVELOPING']
**genre** | **str** |  | [optional] [default to 'OTHER']
**years_active** | **int** |  | [optional] [default to 5]
**territory** | **str** |  | [optional] [default to 'US']

## Example

```python
from xr7_sdk.models.estimate_request import EstimateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of EstimateRequest from a JSON string
estimate_request_instance = EstimateRequest.from_json(json)
# print the JSON string representation of the object
print(EstimateRequest.to_json())

# convert the object into a dict
estimate_request_dict = estimate_request_instance.to_dict()
# create an instance of EstimateRequest from a dict
estimate_request_from_dict = EstimateRequest.from_dict(estimate_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
