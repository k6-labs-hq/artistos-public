# TVFilmForecastRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anomaly_ids** | **List[str]** |  | [optional]
**confidence_override** | **float** |  | [optional]

## Example

```python
from xr7_sdk.models.tv_film_forecast_request import TVFilmForecastRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TVFilmForecastRequest from a JSON string
tv_film_forecast_request_instance = TVFilmForecastRequest.from_json(json)
# print the JSON string representation of the object
print(TVFilmForecastRequest.to_json())

# convert the object into a dict
tv_film_forecast_request_dict = tv_film_forecast_request_instance.to_dict()
# create an instance of TVFilmForecastRequest from a dict
tv_film_forecast_request_from_dict = TVFilmForecastRequest.from_dict(tv_film_forecast_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
