# SupportChatResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  | 
**thread_id** | **str** |  | 
**response** | **str** |  | 
**confidence** | **float** |  | 
**suggested_quick_replies** | **List[str]** |  | 
**escalate_recommended** | **bool** |  | 

## Example

```python
from xr7_sdk.models.support_chat_response import SupportChatResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SupportChatResponse from a JSON string
support_chat_response_instance = SupportChatResponse.from_json(json)
# print the JSON string representation of the object
print(SupportChatResponse.to_json())

# convert the object into a dict
support_chat_response_dict = support_chat_response_instance.to_dict()
# create an instance of SupportChatResponse from a dict
support_chat_response_from_dict = SupportChatResponse.from_dict(support_chat_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


