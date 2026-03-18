# ArtistLoginRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  | 
**email** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.artist_login_request import ArtistLoginRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ArtistLoginRequest from a JSON string
artist_login_request_instance = ArtistLoginRequest.from_json(json)
# print the JSON string representation of the object
print(ArtistLoginRequest.to_json())

# convert the object into a dict
artist_login_request_dict = artist_login_request_instance.to_dict()
# create an instance of ArtistLoginRequest from a dict
artist_login_request_from_dict = ArtistLoginRequest.from_dict(artist_login_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


