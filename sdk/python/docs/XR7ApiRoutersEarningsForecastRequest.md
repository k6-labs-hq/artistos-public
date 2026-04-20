# XR7ApiRoutersEarningsForecastRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**horizon_days** | **int** |  | [optional] [default to 90]
**confidence** | **float** |  | [optional] [default to 0.95]
**by_category** | **bool** |  | [optional] [default to False]

## Example

```python
from xr7_sdk.models.xr7_api_routers_earnings_forecast_request import XR7ApiRoutersEarningsForecastRequest

# TODO update the JSON string below
json = "{}"
# create an instance of XR7ApiRoutersEarningsForecastRequest from a JSON string
xr7_api_routers_earnings_forecast_request_instance = XR7ApiRoutersEarningsForecastRequest.from_json(json)
# print the JSON string representation of the object
print(XR7ApiRoutersEarningsForecastRequest.to_json())

# convert the object into a dict
xr7_api_routers_earnings_forecast_request_dict = xr7_api_routers_earnings_forecast_request_instance.to_dict()
# create an instance of XR7ApiRoutersEarningsForecastRequest from a dict
xr7_api_routers_earnings_forecast_request_from_dict = XR7ApiRoutersEarningsForecastRequest.from_dict(xr7_api_routers_earnings_forecast_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
