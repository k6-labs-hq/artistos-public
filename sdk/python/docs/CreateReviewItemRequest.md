# CreateReviewItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  | 
**source_type** | [**ReviewSourceType**](ReviewSourceType.md) |  | 
**source_id** | **str** |  | [optional] 
**reason** | **str** |  | 
**priority_score** | **float** |  | [optional] [default to 0.0]
**payload** | **Dict[str, object]** |  | [optional] 

## Example

```python
from xr7_sdk.models.create_review_item_request import CreateReviewItemRequest

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of CreateReviewItemRequest from a JSON string
create_review_item_request_instance = CreateReviewItemRequest.from_json(json)
# print the JSON string representation of the object
print(CreateReviewItemRequest.to_json())

# convert the object into a dict
create_review_item_request_dict = create_review_item_request_instance.to_dict()
# create an instance of CreateReviewItemRequest from a dict
create_review_item_request_from_dict = CreateReviewItemRequest.from_dict(create_review_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


