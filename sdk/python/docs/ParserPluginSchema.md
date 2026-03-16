# ParserPluginSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**parser_type** | **str** |  | 
**plugin_name** | **str** |  | 
**plugin_entrypoint** | **str** |  | 
**plugin_signature** | **str** |  | 
**enabled** | **bool** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.parser_plugin_schema import ParserPluginSchema

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of ParserPluginSchema from a JSON string
parser_plugin_schema_instance = ParserPluginSchema.from_json(json)
# print the JSON string representation of the object
print(ParserPluginSchema.to_json())

# convert the object into a dict
parser_plugin_schema_dict = parser_plugin_schema_instance.to_dict()
# create an instance of ParserPluginSchema from a dict
parser_plugin_schema_from_dict = ParserPluginSchema.from_dict(parser_plugin_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


