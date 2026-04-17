# AssignReviewItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**analyst_email** | **str** |  |

## Example

```python
from xr7_sdk.models.assign_review_item_request import AssignReviewItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AssignReviewItemRequest from a JSON string
assign_review_item_request_instance = AssignReviewItemRequest.from_json(json)
# print the JSON string representation of the object
print(AssignReviewItemRequest.to_json())

# convert the object into a dict
assign_review_item_request_dict = assign_review_item_request_instance.to_dict()
# create an instance of AssignReviewItemRequest from a dict
assign_review_item_request_from_dict = AssignReviewItemRequest.from_dict(assign_review_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
