# NotificationPreferenceSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**notify_anomaly_detected** | **bool** |  | 
**notify_urgent_sol** | **bool** |  | 
**notify_deposit_received** | **bool** |  | 
**notify_claim_advanced** | **bool** |  | 
**quiet_hours_start** | **str** |  | [optional] 
**quiet_hours_end** | **str** |  | [optional] 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.notification_preference_schema import NotificationPreferenceSchema

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationPreferenceSchema from a JSON string
notification_preference_schema_instance = NotificationPreferenceSchema.from_json(json)
# print the JSON string representation of the object
print(NotificationPreferenceSchema.to_json())

# convert the object into a dict
notification_preference_schema_dict = notification_preference_schema_instance.to_dict()
# create an instance of NotificationPreferenceSchema from a dict
notification_preference_schema_from_dict = NotificationPreferenceSchema.from_dict(notification_preference_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


