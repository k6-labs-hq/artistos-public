# TaxOptimizerRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gross_amount** | **float** |  | 
**us_withholding_rate** | **float** |  | [optional] [default to 0.3]
**global_withholding_rate** | **float** |  | [optional] [default to 0.1]
**fx_rate** | **float** |  | [optional] [default to 1.0]

## Example

```python
from xr7_sdk.models.tax_optimizer_request import TaxOptimizerRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TaxOptimizerRequest from a JSON string
tax_optimizer_request_instance = TaxOptimizerRequest.from_json(json)
# print the JSON string representation of the object
print(TaxOptimizerRequest.to_json())

# convert the object into a dict
tax_optimizer_request_dict = tax_optimizer_request_instance.to_dict()
# create an instance of TaxOptimizerRequest from a dict
tax_optimizer_request_from_dict = TaxOptimizerRequest.from_dict(tax_optimizer_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


