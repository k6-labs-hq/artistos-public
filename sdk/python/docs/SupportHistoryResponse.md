# SupportHistoryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total** | **int** |  | 
**page** | **int** |  | 
**page_size** | **int** |  | 
**next_cursor** | **str** |  | [optional] 
**items** | [**List[SupportMessageView]**](SupportMessageView.md) |  | 

## Example

```python
from xr7_sdk.models.support_history_response import SupportHistoryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SupportHistoryResponse from a JSON string
support_history_response_instance = SupportHistoryResponse.from_json(json)
# print the JSON string representation of the object
print(SupportHistoryResponse.to_json())

# convert the object into a dict
support_history_response_dict = support_history_response_instance.to_dict()
# create an instance of SupportHistoryResponse from a dict
support_history_response_from_dict = SupportHistoryResponse.from_dict(support_history_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


