# ReviewItemSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  |
**artist_id** | **str** |  |
**source_type** | **str** |  |
**source_id** | **str** |  | [optional]
**reason** | **str** |  |
**priority_score** | **float** |  |
**status** | [**ReviewItemStatus**](ReviewItemStatus.md) |  |
**assigned_analyst_email** | **str** |  | [optional]
**payload** | **Dict[str, object]** |  | [optional]
**created_at** | **datetime** |  |
**updated_at** | **datetime** |  |
**resolved_at** | **datetime** |  | [optional]

## Example

```python
from xr7_sdk.models.review_item_schema import ReviewItemSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ReviewItemSchema from a JSON string
review_item_schema_instance = ReviewItemSchema.from_json(json)
# print the JSON string representation of the object
print(ReviewItemSchema.to_json())

# convert the object into a dict
review_item_schema_dict = review_item_schema_instance.to_dict()
# create an instance of ReviewItemSchema from a dict
review_item_schema_from_dict = ReviewItemSchema.from_dict(review_item_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
