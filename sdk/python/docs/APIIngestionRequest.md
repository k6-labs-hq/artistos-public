# APIIngestionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tenant_id** | **str** |  | [optional] [default to 'default']
**providers** | **List[str]** |  | [optional]
**since** | **datetime** |  | [optional]
**until** | **datetime** |  | [optional]
**queue_backend** | **str** |  | [optional] [default to 'celery']

## Example

```python
from xr7_sdk.models.api_ingestion_request import APIIngestionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of APIIngestionRequest from a JSON string
api_ingestion_request_instance = APIIngestionRequest.from_json(json)
# print the JSON string representation of the object
print(APIIngestionRequest.to_json())

# convert the object into a dict
api_ingestion_request_dict = api_ingestion_request_instance.to_dict()
# create an instance of APIIngestionRequest from a dict
api_ingestion_request_from_dict = APIIngestionRequest.from_dict(api_ingestion_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
