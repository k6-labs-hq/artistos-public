# MLFeedbackEventSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**feedback_type** | [**MLFeedbackType**](MLFeedbackType.md) |  | 
**source_type** | **str** |  | [optional] 
**source_id** | **str** |  | [optional] 
**anomaly_id** | **str** |  | [optional] 
**claim_id** | **str** |  | [optional] 
**subtype** | **str** |  | [optional] 
**category** | **str** |  | [optional] 
**artist_profile_segment** | **str** |  | [optional] 
**model_version** | **str** |  | [optional] 
**model_prediction** | **float** |  | [optional] 
**human_decision** | **str** |  | [optional] 
**outcome** | **str** |  | [optional] 
**estimated_amount** | **float** |  | [optional] 
**actual_amount** | **float** |  | [optional] 
**payload** | **Dict[str, object]** |  | [optional] 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.ml_feedback_event_schema import MLFeedbackEventSchema

# TODO update the JSON string below
json = "{}"
# create an instance of MLFeedbackEventSchema from a JSON string
ml_feedback_event_schema_instance = MLFeedbackEventSchema.from_json(json)
# print the JSON string representation of the object
print(MLFeedbackEventSchema.to_json())

# convert the object into a dict
ml_feedback_event_schema_dict = ml_feedback_event_schema_instance.to_dict()
# create an instance of MLFeedbackEventSchema from a dict
ml_feedback_event_schema_from_dict = MLFeedbackEventSchema.from_dict(ml_feedback_event_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


