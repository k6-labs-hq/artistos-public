# PredictRecoverableRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**catalog_size** | **int** |  | [optional] 
**genre** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.predict_recoverable_request import PredictRecoverableRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PredictRecoverableRequest from a JSON string
predict_recoverable_request_instance = PredictRecoverableRequest.from_json(json)
# print the JSON string representation of the object
print(PredictRecoverableRequest.to_json())

# convert the object into a dict
predict_recoverable_request_dict = predict_recoverable_request_instance.to_dict()
# create an instance of PredictRecoverableRequest from a dict
predict_recoverable_request_from_dict = PredictRecoverableRequest.from_dict(predict_recoverable_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


