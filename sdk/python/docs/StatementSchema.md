# StatementSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**filename** | **str** |  | 
**file_hash** | **str** |  | 
**format_detected** | **str** |  | 
**row_count** | **int** |  | 
**events_created** | **int** |  | 
**payments_created** | **int** |  | 
**skipped_rows** | **int** |  | 
**status** | **str** |  | 
**error_summary** | **str** |  | 
**uploaded_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.statement_schema import StatementSchema

# TODO update the JSON string below
json = "{}"
# create an instance of StatementSchema from a JSON string
statement_schema_instance = StatementSchema.from_json(json)
# print the JSON string representation of the object
print(StatementSchema.to_json())

# convert the object into a dict
statement_schema_dict = statement_schema_instance.to_dict()
# create an instance of StatementSchema from a dict
statement_schema_from_dict = StatementSchema.from_dict(statement_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


