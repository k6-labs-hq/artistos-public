# UtilityRankRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | **List[Dict[str, object]]** |  |
**analyst_hourly_cost** | **float** |  | [optional] [default to 75.0]

## Example

```python
from xr7_sdk.models.utility_rank_request import UtilityRankRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UtilityRankRequest from a JSON string
utility_rank_request_instance = UtilityRankRequest.from_json(json)
# print the JSON string representation of the object
print(UtilityRankRequest.to_json())

# convert the object into a dict
utility_rank_request_dict = utility_rank_request_instance.to_dict()
# create an instance of UtilityRankRequest from a dict
utility_rank_request_from_dict = UtilityRankRequest.from_dict(utility_rank_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
