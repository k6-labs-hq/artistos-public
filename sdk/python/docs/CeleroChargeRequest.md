# CeleroChargeRequest

Charge the artist's Celero vault for a specific claim's contingency fee.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**claim_id** | **str** |  | 
**ip_address** | **str** |  | [optional] [default to '']

## Example

```python
from xr7_sdk.models.celero_charge_request import CeleroChargeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CeleroChargeRequest from a JSON string
celero_charge_request_instance = CeleroChargeRequest.from_json(json)
# print the JSON string representation of the object
print(CeleroChargeRequest.to_json())

# convert the object into a dict
celero_charge_request_dict = celero_charge_request_instance.to_dict()
# create an instance of CeleroChargeRequest from a dict
celero_charge_request_from_dict = CeleroChargeRequest.from_dict(celero_charge_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


