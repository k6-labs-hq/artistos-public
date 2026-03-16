# CeleroRefundRequest

Refund a previous charge, optionally for a partial amount.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 

## Example

```python
from xr7_sdk.models.celero_refund_request import CeleroRefundRequest

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of CeleroRefundRequest from a JSON string
celero_refund_request_instance = CeleroRefundRequest.from_json(json)
# print the JSON string representation of the object
print(CeleroRefundRequest.to_json())

# convert the object into a dict
celero_refund_request_dict = celero_refund_request_instance.to_dict()
# create an instance of CeleroRefundRequest from a dict
celero_refund_request_from_dict = CeleroRefundRequest.from_dict(celero_refund_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


