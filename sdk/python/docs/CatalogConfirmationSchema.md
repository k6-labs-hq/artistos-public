# CatalogConfirmationSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**work_id** | **str** |  | 
**ownership_confirmed** | **str** |  | 
**splits_confirmed** | **str** |  | 
**publisher_confirmed** | **str** |  | 
**admin_confirmed** | **str** |  | 
**correction_notes** | **str** |  | 
**confirmed_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.catalog_confirmation_schema import CatalogConfirmationSchema

# TODO update the JSON string below
json = "{}"
# create an instance of CatalogConfirmationSchema from a JSON string
catalog_confirmation_schema_instance = CatalogConfirmationSchema.from_json(json)
# print the JSON string representation of the object
print(CatalogConfirmationSchema.to_json())

# convert the object into a dict
catalog_confirmation_schema_dict = catalog_confirmation_schema_instance.to_dict()
# create an instance of CatalogConfirmationSchema from a dict
catalog_confirmation_schema_from_dict = CatalogConfirmationSchema.from_dict(catalog_confirmation_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


