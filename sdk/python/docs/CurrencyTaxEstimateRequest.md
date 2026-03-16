# CurrencyTaxEstimateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gross_amount** | **float** |  | 
**source_currency** | **str** |  | [optional] [default to 'USD']
**payout_currency** | **str** |  | [optional] [default to 'USD']
**fx_rate** | **float** |  | [optional] [default to 1.0]
**withholding_rate** | **float** |  | [optional] [default to 0.0]

## Example

```python
from xr7_sdk.models.currency_tax_estimate_request import CurrencyTaxEstimateRequest

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of CurrencyTaxEstimateRequest from a JSON string
currency_tax_estimate_request_instance = CurrencyTaxEstimateRequest.from_json(json)
# print the JSON string representation of the object
print(CurrencyTaxEstimateRequest.to_json())

# convert the object into a dict
currency_tax_estimate_request_dict = currency_tax_estimate_request_instance.to_dict()
# create an instance of CurrencyTaxEstimateRequest from a dict
currency_tax_estimate_request_from_dict = CurrencyTaxEstimateRequest.from_dict(currency_tax_estimate_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


