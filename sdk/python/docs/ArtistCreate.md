# ArtistCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  |
**email** | **str** |  | [optional]
**first_name** | **str** |  | [optional]
**last_name** | **str** |  | [optional]
**country_code** | **str** |  | [optional] [default to 'US']
**role** | **str** |  | [optional]
**ipi_number** | **str** |  | [optional]
**stage_names** | **List[str]** |  | [optional]
**default_attorney_grace_period_days** | **int** |  | [optional] [default to 60]
**primary_jurisdiction** | **str** |  | [optional] [default to 'USA']
**preferred_contract_type** | **str** |  | [optional] [default to 'recording']
**primary_vertical** | **str** |  | [optional]
**tvfilm_role** | **str** |  | [optional]
**organization_type** | **str** |  | [optional]
**enterprise_mode_enabled** | **bool** |  | [optional] [default to False]

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
