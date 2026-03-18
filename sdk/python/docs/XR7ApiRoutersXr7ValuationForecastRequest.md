# XR7ApiRoutersXr7ValuationForecastRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tenant_id** | **str** |  | [optional] [default to 'default']
**horizon_days** | **int** |  | [optional] [default to 90]
**scenario_overrides** | **Dict[str, object]** |  | [optional] 

## Example

```python
from xr7_sdk.models.xr7_api_routers_xr7_valuation_forecast_request import XR7ApiRoutersXr7ValuationForecastRequest

# TODO update the JSON string below
json = "{}"
# create an instance of XR7ApiRoutersXr7ValuationForecastRequest from a JSON string
xr7_api_routers_xr7_valuation_forecast_request_instance = XR7ApiRoutersXr7ValuationForecastRequest.from_json(json)
# print the JSON string representation of the object
print(XR7ApiRoutersXr7ValuationForecastRequest.to_json())

# convert the object into a dict
xr7_api_routers_xr7_valuation_forecast_request_dict = xr7_api_routers_xr7_valuation_forecast_request_instance.to_dict()
# create an instance of XR7ApiRoutersXr7ValuationForecastRequest from a dict
xr7_api_routers_xr7_valuation_forecast_request_from_dict = XR7ApiRoutersXr7ValuationForecastRequest.from_dict(xr7_api_routers_xr7_valuation_forecast_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


