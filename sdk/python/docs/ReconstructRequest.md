# ReconstructRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start_date** | **datetime** |  | 
**end_date** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.reconstruct_request import ReconstructRequest

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of ReconstructRequest from a JSON string
reconstruct_request_instance = ReconstructRequest.from_json(json)
# print the JSON string representation of the object
print(ReconstructRequest.to_json())

# convert the object into a dict
reconstruct_request_dict = reconstruct_request_instance.to_dict()
# create an instance of ReconstructRequest from a dict
reconstruct_request_from_dict = ReconstructRequest.from_dict(reconstruct_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


