# DemandLetterResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  |
**claim_id** | **str** |  | [optional]
**markdown** | **str** |  |
**evidence_zip_link** | **str** |  | [optional]

## Example

```python
from xr7_sdk.models.demand_letter_response import DemandLetterResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DemandLetterResponse from a JSON string
demand_letter_response_instance = DemandLetterResponse.from_json(json)
# print the JSON string representation of the object
print(DemandLetterResponse.to_json())

# convert the object into a dict
demand_letter_response_dict = demand_letter_response_instance.to_dict()
# create an instance of DemandLetterResponse from a dict
demand_letter_response_from_dict = DemandLetterResponse.from_dict(demand_letter_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
