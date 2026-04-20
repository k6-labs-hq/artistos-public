# OAuthTokenRefreshRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rotate_refresh_token** | **bool** |  | [optional] [default to False]
**expires_in_seconds** | **int** |  | [optional] [default to 3600]
**force** | **bool** |  | [optional] [default to False]

## Example

```python
from xr7_sdk.models.o_auth_token_refresh_request import OAuthTokenRefreshRequest

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthTokenRefreshRequest from a JSON string
o_auth_token_refresh_request_instance = OAuthTokenRefreshRequest.from_json(json)
# print the JSON string representation of the object
print(OAuthTokenRefreshRequest.to_json())

# convert the object into a dict
o_auth_token_refresh_request_dict = o_auth_token_refresh_request_instance.to_dict()
# create an instance of OAuthTokenRefreshRequest from a dict
o_auth_token_refresh_request_from_dict = OAuthTokenRefreshRequest.from_dict(o_auth_token_refresh_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
