# CreatorIngestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**platform** | **str** |  | 
**rows** | **List[Dict[str, object]]** |  | 

## Example

```python
from xr7_sdk.models.creator_ingest_request import CreatorIngestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatorIngestRequest from a JSON string
creator_ingest_request_instance = CreatorIngestRequest.from_json(json)
# print the JSON string representation of the object
print(CreatorIngestRequest.to_json())

# convert the object into a dict
creator_ingest_request_dict = creator_ingest_request_instance.to_dict()
# create an instance of CreatorIngestRequest from a dict
creator_ingest_request_from_dict = CreatorIngestRequest.from_dict(creator_ingest_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


