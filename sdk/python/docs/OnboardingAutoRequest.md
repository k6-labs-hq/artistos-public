# OnboardingAutoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**run_due_sync_jobs_now** | **bool** |  | [optional] [default to True]

## Example

```python
from xr7_sdk.models.onboarding_auto_request import OnboardingAutoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of OnboardingAutoRequest from a JSON string
onboarding_auto_request_instance = OnboardingAutoRequest.from_json(json)
# print the JSON string representation of the object
print(OnboardingAutoRequest.to_json())

# convert the object into a dict
onboarding_auto_request_dict = onboarding_auto_request_instance.to_dict()
# create an instance of OnboardingAutoRequest from a dict
onboarding_auto_request_from_dict = OnboardingAutoRequest.from_dict(onboarding_auto_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
