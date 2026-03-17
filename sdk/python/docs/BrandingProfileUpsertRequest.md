# BrandingProfileUpsertRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** |  | [optional] [default to 'XR7']
**logo_url** | **str** |  | [optional] [default to 'https://assets.xr7.ai/logo.svg']
**primary_color** | **str** |  | [optional] [default to '#1f7a5a']
**secondary_color** | **str** |  | [optional] [default to '#2f9c74']
**accent_color** | **str** |  | [optional] [default to '#f59e0b']
**dashboard_header_text** | **str** |  | [optional] [default to 'Artist Recovery Dashboard']
**dashboard_footer_text** | **str** |  | [optional] [default to 'Powered by XR7 Engine']
**support_email** | **str** |  | [optional] [default to 'support@xr7.ai']
**support_phone** | **str** |  | [optional] [default to '+1-800-XR7-HELP']
**legal_disclaimer** | **str** |  | [optional] [default to 'Forecasts and recovery estimates are provided for operational guidance only. Actual outcomes may vary based on payer behavior, legal deadlines, and data quality.']
**custom_domain** | **str** |  | [optional] 
**white_label_enabled** | **bool** |  | [optional] [default to False]

## Example

```python
from xr7_sdk.models.branding_profile_upsert_request import BrandingProfileUpsertRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BrandingProfileUpsertRequest from a JSON string
branding_profile_upsert_request_instance = BrandingProfileUpsertRequest.from_json(json)
# print the JSON string representation of the object
print(BrandingProfileUpsertRequest.to_json())

# convert the object into a dict
branding_profile_upsert_request_dict = branding_profile_upsert_request_instance.to_dict()
# create an instance of BrandingProfileUpsertRequest from a dict
branding_profile_upsert_request_from_dict = BrandingProfileUpsertRequest.from_dict(branding_profile_upsert_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


