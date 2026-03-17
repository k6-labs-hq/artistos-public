# RecoveryOutcomeFeedbackSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**anomaly_id** | **str** |  | 
**claim_id** | **str** |  | 
**outcome** | [**FeedbackOutcome**](FeedbackOutcome.md) |  | 
**recovered_amount** | **float** |  | 
**reason_code** | **str** |  | 
**analyst_note** | **str** |  | 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.recovery_outcome_feedback_schema import RecoveryOutcomeFeedbackSchema

# TODO update the JSON string below
json = "{}"
# create an instance of RecoveryOutcomeFeedbackSchema from a JSON string
recovery_outcome_feedback_schema_instance = RecoveryOutcomeFeedbackSchema.from_json(json)
# print the JSON string representation of the object
print(RecoveryOutcomeFeedbackSchema.to_json())

# convert the object into a dict
recovery_outcome_feedback_schema_dict = recovery_outcome_feedback_schema_instance.to_dict()
# create an instance of RecoveryOutcomeFeedbackSchema from a dict
recovery_outcome_feedback_schema_from_dict = RecoveryOutcomeFeedbackSchema.from_dict(recovery_outcome_feedback_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


