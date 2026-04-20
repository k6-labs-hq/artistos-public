# OAuthSessionCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**provider** | **str** |  |
**redirect_uri** | **str** |  |
**scopes** | **List[str]** |  | [optional]
**tenant_id** | **str** |  | [optional] [default to 'default']

## Example

```python
from xr7_sdk.models.o_auth_session_create_request import OAuthSessionCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthSessionCreateRequest from a JSON string
o_auth_session_create_request_instance = OAuthSessionCreateRequest.from_json(json)
# print the JSON string representation of the object
print(OAuthSessionCreateRequest.to_json())

# convert the object into a dict
o_auth_session_create_request_dict = o_auth_session_create_request_instance.to_dict()
# create an instance of OAuthSessionCreateRequest from a dict
o_auth_session_create_request_from_dict = OAuthSessionCreateRequest.from_dict(o_auth_session_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
