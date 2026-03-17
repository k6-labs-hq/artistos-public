# AdviceResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  | 
**response** | **str** |  | 
**conversation_history** | **List[Dict[str, str]]** |  | 

## Example

```python
from xr7_sdk.models.advice_response import AdviceResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AdviceResponse from a JSON string
advice_response_instance = AdviceResponse.from_json(json)
# print the JSON string representation of the object
print(AdviceResponse.to_json())

# convert the object into a dict
advice_response_dict = advice_response_instance.to_dict()
# create an instance of AdviceResponse from a dict
advice_response_from_dict = AdviceResponse.from_dict(advice_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


