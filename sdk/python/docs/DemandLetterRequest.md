# DemandLetterRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**claim_id** | **str** |  | [optional] 
**anomaly** | **Dict[str, object]** |  | [optional] 
**evidence** | **Dict[str, object]** |  | [optional] 

## Example

```python
from xr7_sdk.models.demand_letter_request import DemandLetterRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DemandLetterRequest from a JSON string
demand_letter_request_instance = DemandLetterRequest.from_json(json)
# print the JSON string representation of the object
print(DemandLetterRequest.to_json())

# convert the object into a dict
demand_letter_request_dict = demand_letter_request_instance.to_dict()
# create an instance of DemandLetterRequest from a dict
demand_letter_request_from_dict = DemandLetterRequest.from_dict(demand_letter_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


