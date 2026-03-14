# RecoveryOutcomeFeedbackCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anomaly_id** | **str** |  | [optional] 
**claim_id** | **str** |  | [optional] 
**outcome** | [**FeedbackOutcome**](FeedbackOutcome.md) |  | 
**recovered_amount** | **float** |  | [optional] 
**reason_code** | **str** |  | [optional] 
**analyst_note** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.recovery_outcome_feedback_create import RecoveryOutcomeFeedbackCreate

# TODO update the JSON string below
json = "{}"
# create an instance of RecoveryOutcomeFeedbackCreate from a JSON string
recovery_outcome_feedback_create_instance = RecoveryOutcomeFeedbackCreate.from_json(json)
# print the JSON string representation of the object
print(RecoveryOutcomeFeedbackCreate.to_json())

# convert the object into a dict
recovery_outcome_feedback_create_dict = recovery_outcome_feedback_create_instance.to_dict()
# create an instance of RecoveryOutcomeFeedbackCreate from a dict
recovery_outcome_feedback_create_from_dict = RecoveryOutcomeFeedbackCreate.from_dict(recovery_outcome_feedback_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


