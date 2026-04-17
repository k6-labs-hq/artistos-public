# IdentityMatchRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**statement_id** | **str** |  | [optional]
**statement_signals** | **Dict[str, object]** |  |

## Example

```python
from xr7_sdk.models.identity_match_request import IdentityMatchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of IdentityMatchRequest from a JSON string
identity_match_request_instance = IdentityMatchRequest.from_json(json)
# print the JSON string representation of the object
print(IdentityMatchRequest.to_json())

# convert the object into a dict
identity_match_request_dict = identity_match_request_instance.to_dict()
# create an instance of IdentityMatchRequest from a dict
identity_match_request_from_dict = IdentityMatchRequest.from_dict(identity_match_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
