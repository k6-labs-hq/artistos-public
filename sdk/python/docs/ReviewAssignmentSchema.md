# ReviewAssignmentSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**review_item_id** | **str** |  | 
**analyst_email** | **str** |  | 
**assigned_at** | **datetime** |  | 
**unassigned_at** | **datetime** |  | [optional] 

## Example

```python
from xr7_sdk.models.review_assignment_schema import ReviewAssignmentSchema

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of ReviewAssignmentSchema from a JSON string
review_assignment_schema_instance = ReviewAssignmentSchema.from_json(json)
# print the JSON string representation of the object
print(ReviewAssignmentSchema.to_json())

# convert the object into a dict
review_assignment_schema_dict = review_assignment_schema_instance.to_dict()
# create an instance of ReviewAssignmentSchema from a dict
review_assignment_schema_from_dict = ReviewAssignmentSchema.from_dict(review_assignment_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


