# RegisterResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **str** |  | 
**message** | **str** |  | 
**expires_in_seconds** | **int** |  | 
**dev_phone_otp** | **str** |  | [optional] 
**dev_email_otp** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.register_response import RegisterResponse

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of RegisterResponse from a JSON string
register_response_instance = RegisterResponse.from_json(json)
# print the JSON string representation of the object
print(RegisterResponse.to_json())

# convert the object into a dict
register_response_dict = register_response_instance.to_dict()
# create an instance of RegisterResponse from a dict
register_response_from_dict = RegisterResponse.from_dict(register_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


