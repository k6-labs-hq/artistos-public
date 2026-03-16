# CeleroDisburseRequest

Disburse a net recovery amount to the artist via ACH.  ``amount`` is the net amount in USD after XR7's fee has been deducted. ``claim_id`` is optional — omit for manual / ad-hoc disbursements.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | 
**currency** | **str** |  | [optional] [default to 'USD']
**claim_id** | **str** |  | [optional] 
**description** | **str** |  | [optional] [default to '']

## Example

```python
from xr7_sdk.models.celero_disburse_request import CeleroDisburseRequest

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of CeleroDisburseRequest from a JSON string
celero_disburse_request_instance = CeleroDisburseRequest.from_json(json)
# print the JSON string representation of the object
print(CeleroDisburseRequest.to_json())

# convert the object into a dict
celero_disburse_request_dict = celero_disburse_request_instance.to_dict()
# create an instance of CeleroDisburseRequest from a dict
celero_disburse_request_from_dict = CeleroDisburseRequest.from_dict(celero_disburse_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


