# CeleroRegisterRequest

Information needed to create an artist as a Celero customer.  Card / bank account details are collected separately via Celero's hosted Collect.js form and never pass through XR7 servers.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | 
**last_name** | **str** |  | 
**email** | **str** |  | 
**company** | **str** |  | [optional] [default to '']
**address1** | **str** |  | [optional] [default to '']
**city** | **str** |  | [optional] [default to '']
**state** | **str** |  | [optional] [default to '']
**zip_code** | **str** |  | [optional] [default to '']
**country** | **str** |  | [optional] [default to 'US']
**phone** | **str** |  | [optional] [default to '']

## Example

```python
from xr7_sdk.models.celero_register_request import CeleroRegisterRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CeleroRegisterRequest from a JSON string
celero_register_request_instance = CeleroRegisterRequest.from_json(json)
# print the JSON string representation of the object
print(CeleroRegisterRequest.to_json())

# convert the object into a dict
celero_register_request_dict = celero_register_request_instance.to_dict()
# create an instance of CeleroRegisterRequest from a dict
celero_register_request_from_dict = CeleroRegisterRequest.from_dict(celero_register_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


