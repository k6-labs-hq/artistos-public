# BlackBoxRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tenant_id** | **str** |  | [optional] [default to 'default']
**min_confidence** | **float** |  | [optional] [default to 0.85]
**queue_backend** | **str** |  | [optional] [default to 'celery']

## Example

```python
from xr7_sdk.models.black_box_request import BlackBoxRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BlackBoxRequest from a JSON string
black_box_request_instance = BlackBoxRequest.from_json(json)
# print the JSON string representation of the object
print(BlackBoxRequest.to_json())

# convert the object into a dict
black_box_request_dict = black_box_request_instance.to_dict()
# create an instance of BlackBoxRequest from a dict
black_box_request_from_dict = BlackBoxRequest.from_dict(black_box_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
