# ArtistSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**ipi_number** | **str** |  | [optional] 
**stage_names** | **List[str]** |  | [optional] 
**created_at** | **datetime** |  | 
**status** | [**ArtistLifecycleStatus**](ArtistLifecycleStatus.md) |  | 
**onboarded_at** | **datetime** |  | [optional] 
**activated_at** | **datetime** |  | [optional] 
**celero_customer_vault_id** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.artist_schema import ArtistSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ArtistSchema from a JSON string
artist_schema_instance = ArtistSchema.from_json(json)
# print the JSON string representation of the object
print(ArtistSchema.to_json())

# convert the object into a dict
artist_schema_dict = artist_schema_instance.to_dict()
# create an instance of ArtistSchema from a dict
artist_schema_from_dict = ArtistSchema.from_dict(artist_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


