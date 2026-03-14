# VarianceScanRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rows** | **List[Dict[str, object]]** |  | 

## Example

```python
from xr7_sdk.models.variance_scan_request import VarianceScanRequest

# TODO update the JSON string below
json = "{}"
# create an instance of VarianceScanRequest from a JSON string
variance_scan_request_instance = VarianceScanRequest.from_json(json)
# print the JSON string representation of the object
print(VarianceScanRequest.to_json())

# convert the object into a dict
variance_scan_request_dict = variance_scan_request_instance.to_dict()
# create an instance of VarianceScanRequest from a dict
variance_scan_request_from_dict = VarianceScanRequest.from_dict(variance_scan_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


