# NegotiationScriptRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**claim** | **Dict[str, object]** |  | [optional]

## Example

```python
from xr7_sdk.models.negotiation_script_request import NegotiationScriptRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NegotiationScriptRequest from a JSON string
negotiation_script_request_instance = NegotiationScriptRequest.from_json(json)
# print the JSON string representation of the object
print(NegotiationScriptRequest.to_json())

# convert the object into a dict
negotiation_script_request_dict = negotiation_script_request_instance.to_dict()
# create an instance of NegotiationScriptRequest from a dict
negotiation_script_request_from_dict = NegotiationScriptRequest.from_dict(negotiation_script_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
