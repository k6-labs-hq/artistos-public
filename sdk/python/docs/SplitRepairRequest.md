# SplitRepairRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rights_rows** | **List[Dict[str, object]]** |  |
**payout_rows** | **List[Dict[str, object]]** |  |
**apply_threshold** | **float** |  | [optional] [default to 0.85]

## Example

```python
from xr7_sdk.models.split_repair_request import SplitRepairRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SplitRepairRequest from a JSON string
split_repair_request_instance = SplitRepairRequest.from_json(json)
# print the JSON string representation of the object
print(SplitRepairRequest.to_json())

# convert the object into a dict
split_repair_request_dict = split_repair_request_instance.to_dict()
# create an instance of SplitRepairRequest from a dict
split_repair_request_from_dict = SplitRepairRequest.from_dict(split_repair_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
