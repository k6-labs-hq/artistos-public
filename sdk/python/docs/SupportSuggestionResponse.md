# SupportSuggestionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  | 
**suggestions** | **List[str]** |  | 

## Example

```python
from xr7_sdk.models.support_suggestion_response import SupportSuggestionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SupportSuggestionResponse from a JSON string
support_suggestion_response_instance = SupportSuggestionResponse.from_json(json)
# print the JSON string representation of the object
print(SupportSuggestionResponse.to_json())

# convert the object into a dict
support_suggestion_response_dict = support_suggestion_response_instance.to_dict()
# create an instance of SupportSuggestionResponse from a dict
support_suggestion_response_from_dict = SupportSuggestionResponse.from_dict(support_suggestion_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


