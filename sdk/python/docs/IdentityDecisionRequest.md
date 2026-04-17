# IdentityDecisionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**decision** | [**IdentityDecisionStatus**](IdentityDecisionStatus.md) |  |
**actor** | **str** |  |
**reason** | **str** |  |

## Example

```python
from xr7_sdk.models.identity_decision_request import IdentityDecisionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of IdentityDecisionRequest from a JSON string
identity_decision_request_instance = IdentityDecisionRequest.from_json(json)
# print the JSON string representation of the object
print(IdentityDecisionRequest.to_json())

# convert the object into a dict
identity_decision_request_dict = identity_decision_request_instance.to_dict()
# create an instance of IdentityDecisionRequest from a dict
identity_decision_request_from_dict = IdentityDecisionRequest.from_dict(identity_decision_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
