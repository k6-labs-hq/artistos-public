# SupportActionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  |
**action** | **str** |  |
**result** | **Dict[str, object]** |  |
**formatted_message** | **str** |  |

## Example

```python
from xr7_sdk.models.support_action_response import SupportActionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SupportActionResponse from a JSON string
support_action_response_instance = SupportActionResponse.from_json(json)
# print the JSON string representation of the object
print(SupportActionResponse.to_json())

# convert the object into a dict
support_action_response_dict = support_action_response_instance.to_dict()
# create an instance of SupportActionResponse from a dict
support_action_response_from_dict = SupportActionResponse.from_dict(support_action_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
