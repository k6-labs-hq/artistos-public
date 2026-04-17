# MetadataRepairSuggestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tenant_id** | **str** |  | [optional] [default to 'default']
**scope** | **str** |  | [optional] [default to 'catalog']
**max_items** | **int** |  | [optional] [default to 50]

## Example

```python
from xr7_sdk.models.metadata_repair_suggest_request import MetadataRepairSuggestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MetadataRepairSuggestRequest from a JSON string
metadata_repair_suggest_request_instance = MetadataRepairSuggestRequest.from_json(json)
# print the JSON string representation of the object
print(MetadataRepairSuggestRequest.to_json())

# convert the object into a dict
metadata_repair_suggest_request_dict = metadata_repair_suggest_request_instance.to_dict()
# create an instance of MetadataRepairSuggestRequest from a dict
metadata_repair_suggest_request_from_dict = MetadataRepairSuggestRequest.from_dict(metadata_repair_suggest_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
