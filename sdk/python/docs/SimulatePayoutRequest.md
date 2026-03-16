# SimulatePayoutRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**usage_rows** | **List[Dict[str, object]]** |  | 
**fallback_rate** | **float** |  | [optional] [default to 0.004]
**default_withholding_rate** | **float** |  | [optional] [default to 0.0]
**default_fx_rate** | **float** |  | [optional] [default to 1.0]
**payout_currency** | **str** |  | [optional] [default to 'USD']
**received_amount** | **float** |  | [optional] 
**contract_terms** | **Dict[str, object]** |  | [optional] 

## Example

```python
from xr7_sdk.models.simulate_payout_request import SimulatePayoutRequest

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of SimulatePayoutRequest from a JSON string
simulate_payout_request_instance = SimulatePayoutRequest.from_json(json)
# print the JSON string representation of the object
print(SimulatePayoutRequest.to_json())

# convert the object into a dict
simulate_payout_request_dict = simulate_payout_request_instance.to_dict()
# create an instance of SimulatePayoutRequest from a dict
simulate_payout_request_from_dict = SimulatePayoutRequest.from_dict(simulate_payout_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


