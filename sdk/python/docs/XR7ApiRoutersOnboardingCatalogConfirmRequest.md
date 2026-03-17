# XR7ApiRoutersOnboardingCatalogConfirmRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**work_id** | **str** |  | 
**ownership_confirmed** | **str** |  | [optional] [default to 'confirmed']
**splits_confirmed** | **str** |  | [optional] [default to 'confirmed']
**publisher_confirmed** | **str** |  | [optional] [default to 'confirmed']
**admin_confirmed** | **str** |  | [optional] [default to 'confirmed']
**correction_notes** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.xr7_api_routers_onboarding_catalog_confirm_request import XR7ApiRoutersOnboardingCatalogConfirmRequest

# TODO update the JSON string below
json = "{}"
# create an instance of XR7ApiRoutersOnboardingCatalogConfirmRequest from a JSON string
xr7_api_routers_onboarding_catalog_confirm_request_instance = XR7ApiRoutersOnboardingCatalogConfirmRequest.from_json(json)
# print the JSON string representation of the object
print(XR7ApiRoutersOnboardingCatalogConfirmRequest.to_json())

# convert the object into a dict
xr7_api_routers_onboarding_catalog_confirm_request_dict = xr7_api_routers_onboarding_catalog_confirm_request_instance.to_dict()
# create an instance of XR7ApiRoutersOnboardingCatalogConfirmRequest from a dict
xr7_api_routers_onboarding_catalog_confirm_request_from_dict = XR7ApiRoutersOnboardingCatalogConfirmRequest.from_dict(xr7_api_routers_onboarding_catalog_confirm_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


