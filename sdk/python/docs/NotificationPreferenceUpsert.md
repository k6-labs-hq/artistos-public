# NotificationPreferenceUpsert


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**notify_anomaly_detected** | **bool** |  | [optional] [default to True]
**notify_urgent_sol** | **bool** |  | [optional] [default to True]
**notify_deposit_received** | **bool** |  | [optional] [default to True]
**notify_claim_advanced** | **bool** |  | [optional] [default to True]
**quiet_hours_start** | **str** |  | [optional] 
**quiet_hours_end** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.notification_preference_upsert import NotificationPreferenceUpsert

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of NotificationPreferenceUpsert from a JSON string
notification_preference_upsert_instance = NotificationPreferenceUpsert.from_json(json)
# print the JSON string representation of the object
print(NotificationPreferenceUpsert.to_json())

# convert the object into a dict
notification_preference_upsert_dict = notification_preference_upsert_instance.to_dict()
# create an instance of NotificationPreferenceUpsert from a dict
notification_preference_upsert_from_dict = NotificationPreferenceUpsert.from_dict(notification_preference_upsert_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


