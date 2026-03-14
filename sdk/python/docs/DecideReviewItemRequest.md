# DecideReviewItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**decision** | [**ReviewDecisionType**](ReviewDecisionType.md) |  | 
**notes** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.decide_review_item_request import DecideReviewItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DecideReviewItemRequest from a JSON string
decide_review_item_request_instance = DecideReviewItemRequest.from_json(json)
# print the JSON string representation of the object
print(DecideReviewItemRequest.to_json())

# convert the object into a dict
decide_review_item_request_dict = decide_review_item_request_instance.to_dict()
# create an instance of DecideReviewItemRequest from a dict
decide_review_item_request_from_dict = DecideReviewItemRequest.from_dict(decide_review_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


