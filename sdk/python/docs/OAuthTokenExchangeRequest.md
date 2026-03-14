# OAuthTokenExchangeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**state** | **str** |  | 
**code** | **str** |  | 
**external_account_id** | **str** |  | 
**tenant_id** | **str** |  | [optional] [default to 'default']
**granted_scopes** | **List[str]** |  | [optional] 
**allow_partial_scope_grant** | **bool** |  | [optional] [default to False]
**access_token** | **str** |  | [optional] 
**refresh_token** | **str** |  | [optional] 
**token_type** | **str** |  | [optional] [default to 'Bearer']
**expires_in_seconds** | **int** |  | [optional] 
**display_name** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.o_auth_token_exchange_request import OAuthTokenExchangeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthTokenExchangeRequest from a JSON string
o_auth_token_exchange_request_instance = OAuthTokenExchangeRequest.from_json(json)
# print the JSON string representation of the object
print(OAuthTokenExchangeRequest.to_json())

# convert the object into a dict
o_auth_token_exchange_request_dict = o_auth_token_exchange_request_instance.to_dict()
# create an instance of OAuthTokenExchangeRequest from a dict
o_auth_token_exchange_request_from_dict = OAuthTokenExchangeRequest.from_dict(o_auth_token_exchange_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


