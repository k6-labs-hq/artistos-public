# AuthConnectResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**provider** | **str** |  | 
**authorization_url** | **str** |  | 
**configured** | **bool** |  | 
**state** | **str** |  | 

## Example

```python
from xr7_sdk.models.auth_connect_response import AuthConnectResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AuthConnectResponse from a JSON string
auth_connect_response_instance = AuthConnectResponse.from_json(json)
# print the JSON string representation of the object
print(AuthConnectResponse.to_json())

# convert the object into a dict
auth_connect_response_dict = auth_connect_response_instance.to_dict()
# create an instance of AuthConnectResponse from a dict
auth_connect_response_from_dict = AuthConnectResponse.from_dict(auth_connect_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


