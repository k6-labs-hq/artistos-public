# NotificationPreferenceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**notify_anomaly_detected** | **bool** |  | [optional] [default to True]
**notify_urgent_sol** | **bool** |  | [optional] [default to True]
**notify_deposit_received** | **bool** |  | [optional] [default to True]
**notify_claim_advanced** | **bool** |  | [optional] [default to True]
**quiet_hours_start** | **int** |  | [optional] [default to 22]
**quiet_hours_end** | **int** |  | [optional] [default to 7]

## Example

```python
from xr7_sdk.models.notification_preference_request import NotificationPreferenceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationPreferenceRequest from a JSON string
notification_preference_request_instance = NotificationPreferenceRequest.from_json(json)
# print the JSON string representation of the object
print(NotificationPreferenceRequest.to_json())

# convert the object into a dict
notification_preference_request_dict = notification_preference_request_instance.to_dict()
# create an instance of NotificationPreferenceRequest from a dict
notification_preference_request_from_dict = NotificationPreferenceRequest.from_dict(notification_preference_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


