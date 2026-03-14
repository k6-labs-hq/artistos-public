# ArtistCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**ipi_number** | **str** |  | [optional] 
**stage_names** | **List[str]** |  | [optional] 

## Example

```python
from xr7_sdk.models.artist_create import ArtistCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ArtistCreate from a JSON string
artist_create_instance = ArtistCreate.from_json(json)
# print the JSON string representation of the object
print(ArtistCreate.to_json())

# convert the object into a dict
artist_create_dict = artist_create_instance.to_dict()
# create an instance of ArtistCreate from a dict
artist_create_from_dict = ArtistCreate.from_dict(artist_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


