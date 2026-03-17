# ArtistPreferenceUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_attorney_grace_period_days** | **int** |  | [optional] [default to 60]
**primary_jurisdiction** | **str** |  | [optional] [default to 'USA']
**preferred_contract_type** | **str** |  | [optional] [default to 'recording']

## Example

```python
from xr7_sdk.models.artist_preference_update_request import ArtistPreferenceUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ArtistPreferenceUpdateRequest from a JSON string
artist_preference_update_request_instance = ArtistPreferenceUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(ArtistPreferenceUpdateRequest.to_json())

# convert the object into a dict
artist_preference_update_request_dict = artist_preference_update_request_instance.to_dict()
# create an instance of ArtistPreferenceUpdateRequest from a dict
artist_preference_update_request_from_dict = ArtistPreferenceUpdateRequest.from_dict(artist_preference_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


