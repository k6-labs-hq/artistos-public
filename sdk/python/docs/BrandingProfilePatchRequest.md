# BrandingProfilePatchRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** |  | [optional] 
**logo_url** | **str** |  | [optional] 
**primary_color** | **str** |  | [optional] 
**secondary_color** | **str** |  | [optional] 
**accent_color** | **str** |  | [optional] 
**dashboard_header_text** | **str** |  | [optional] 
**dashboard_footer_text** | **str** |  | [optional] 
**support_email** | **str** |  | [optional] 
**support_phone** | **str** |  | [optional] 
**legal_disclaimer** | **str** |  | [optional] 
**custom_domain** | **str** |  | [optional] 
**white_label_enabled** | **bool** |  | [optional] 

## Example

```python
from xr7_sdk.models.branding_profile_patch_request import BrandingProfilePatchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BrandingProfilePatchRequest from a JSON string
branding_profile_patch_request_instance = BrandingProfilePatchRequest.from_json(json)
# print the JSON string representation of the object
print(BrandingProfilePatchRequest.to_json())

# convert the object into a dict
branding_profile_patch_request_dict = branding_profile_patch_request_instance.to_dict()
# create an instance of BrandingProfilePatchRequest from a dict
branding_profile_patch_request_from_dict = BrandingProfilePatchRequest.from_dict(branding_profile_patch_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


