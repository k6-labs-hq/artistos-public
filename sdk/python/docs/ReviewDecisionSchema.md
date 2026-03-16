# ReviewDecisionSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**review_item_id** | **str** |  | 
**analyst_email** | **str** |  | 
**decision** | [**ReviewDecisionType**](ReviewDecisionType.md) |  | 
**notes** | **str** |  | [optional] 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.review_decision_schema import ReviewDecisionSchema

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of ReviewDecisionSchema from a JSON string
review_decision_schema_instance = ReviewDecisionSchema.from_json(json)
# print the JSON string representation of the object
print(ReviewDecisionSchema.to_json())

# convert the object into a dict
review_decision_schema_dict = review_decision_schema_instance.to_dict()
# create an instance of ReviewDecisionSchema from a dict
review_decision_schema_from_dict = ReviewDecisionSchema.from_dict(review_decision_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


