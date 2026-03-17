# NegotiationScriptResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  | 
**claim_id** | **str** |  | [optional] 
**script** | **Dict[str, object]** |  | 

## Example

```python
from xr7_sdk.models.negotiation_script_response import NegotiationScriptResponse

# TODO update the JSON string below
json = "{}"
# create an instance of NegotiationScriptResponse from a JSON string
negotiation_script_response_instance = NegotiationScriptResponse.from_json(json)
# print the JSON string representation of the object
print(NegotiationScriptResponse.to_json())

# convert the object into a dict
negotiation_script_response_dict = negotiation_script_response_instance.to_dict()
# create an instance of NegotiationScriptResponse from a dict
negotiation_script_response_from_dict = NegotiationScriptResponse.from_dict(negotiation_script_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


