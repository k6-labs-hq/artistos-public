# AdvanceOfferRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**predicted_low_forecast** | **float** |  | 
**currency** | **str** |  | [optional] [default to 'USD']
**advance_fee_pct** | **float** |  | [optional] [default to 3.0]

## Example

```python
from xr7_sdk.models.advance_offer_request import AdvanceOfferRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AdvanceOfferRequest from a JSON string
advance_offer_request_instance = AdvanceOfferRequest.from_json(json)
# print the JSON string representation of the object
print(AdvanceOfferRequest.to_json())

# convert the object into a dict
advance_offer_request_dict = advance_offer_request_instance.to_dict()
# create an instance of AdvanceOfferRequest from a dict
advance_offer_request_from_dict = AdvanceOfferRequest.from_dict(advance_offer_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


