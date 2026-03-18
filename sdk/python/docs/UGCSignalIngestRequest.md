# UGCSignalIngestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tenant_id** | **str** |  | [optional] [default to 'default']
**platform** | **str** |  | 
**signals** | **List[Dict[str, object]]** |  | [optional] 

## Example

```python
from xr7_sdk.models.ugc_signal_ingest_request import UGCSignalIngestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UGCSignalIngestRequest from a JSON string
ugc_signal_ingest_request_instance = UGCSignalIngestRequest.from_json(json)
# print the JSON string representation of the object
print(UGCSignalIngestRequest.to_json())

# convert the object into a dict
ugc_signal_ingest_request_dict = ugc_signal_ingest_request_instance.to_dict()
# create an instance of UGCSignalIngestRequest from a dict
ugc_signal_ingest_request_from_dict = UGCSignalIngestRequest.from_dict(ugc_signal_ingest_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


