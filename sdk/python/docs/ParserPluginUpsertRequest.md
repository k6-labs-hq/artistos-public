# ParserPluginUpsertRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parser_type** | **str** |  |
**plugin_name** | **str** |  |
**plugin_entrypoint** | **str** |  |
**plugin_signature** | **str** |  | [optional]
**enabled** | **bool** |  | [optional] [default to True]

## Example

```python
from xr7_sdk.models.parser_plugin_upsert_request import ParserPluginUpsertRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ParserPluginUpsertRequest from a JSON string
parser_plugin_upsert_request_instance = ParserPluginUpsertRequest.from_json(json)
# print the JSON string representation of the object
print(ParserPluginUpsertRequest.to_json())

# convert the object into a dict
parser_plugin_upsert_request_dict = parser_plugin_upsert_request_instance.to_dict()
# create an instance of ParserPluginUpsertRequest from a dict
parser_plugin_upsert_request_from_dict = ParserPluginUpsertRequest.from_dict(parser_plugin_upsert_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
