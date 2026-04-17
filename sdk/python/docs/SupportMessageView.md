# SupportMessageView


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  |
**thread_id** | **str** |  |
**role** | **str** |  |
**message** | **str** |  |
**confidence** | **float** |  | [optional]
**metadata** | **Dict[str, object]** |  | [optional]
**created_at** | **str** |  |

## Example

```python
from xr7_sdk.models.support_message_view import SupportMessageView

# TODO update the JSON string below
json = "{}"
# create an instance of SupportMessageView from a JSON string
support_message_view_instance = SupportMessageView.from_json(json)
# print the JSON string representation of the object
print(SupportMessageView.to_json())

# convert the object into a dict
support_message_view_dict = support_message_view_instance.to_dict()
# create an instance of SupportMessageView from a dict
support_message_view_from_dict = SupportMessageView.from_dict(support_message_view_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
