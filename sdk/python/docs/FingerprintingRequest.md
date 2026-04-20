# FingerprintingRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tenant_id** | **str** |  | [optional] [default to 'default']
**platform** | **str** |  |
**detections** | **List[Dict[str, object]]** |  | [optional]
**queue_backend** | **str** |  | [optional] [default to 'celery']

## Example

```python
from xr7_sdk.models.fingerprinting_request import FingerprintingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FingerprintingRequest from a JSON string
fingerprinting_request_instance = FingerprintingRequest.from_json(json)
# print the JSON string representation of the object
print(FingerprintingRequest.to_json())

# convert the object into a dict
fingerprinting_request_dict = fingerprinting_request_instance.to_dict()
# create an instance of FingerprintingRequest from a dict
fingerprinting_request_from_dict = FingerprintingRequest.from_dict(fingerprinting_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
