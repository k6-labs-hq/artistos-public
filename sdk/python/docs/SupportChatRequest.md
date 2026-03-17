# SupportChatRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** |  | 
**thread_id** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.support_chat_request import SupportChatRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SupportChatRequest from a JSON string
support_chat_request_instance = SupportChatRequest.from_json(json)
# print the JSON string representation of the object
print(SupportChatRequest.to_json())

# convert the object into a dict
support_chat_request_dict = support_chat_request_instance.to_dict()
# create an instance of SupportChatRequest from a dict
support_chat_request_from_dict = SupportChatRequest.from_dict(support_chat_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


