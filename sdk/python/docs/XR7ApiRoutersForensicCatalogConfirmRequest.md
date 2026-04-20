# XR7ApiRoutersForensicCatalogConfirmRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_id** | **str** |  |
**works** | **List[Dict[str, object]]** |  | [optional]

## Example

```python
from xr7_sdk.models.xr7_api_routers_forensic_catalog_confirm_request import XR7ApiRoutersForensicCatalogConfirmRequest

# TODO update the JSON string below
json = "{}"
# create an instance of XR7ApiRoutersForensicCatalogConfirmRequest from a JSON string
xr7_api_routers_forensic_catalog_confirm_request_instance = XR7ApiRoutersForensicCatalogConfirmRequest.from_json(json)
# print the JSON string representation of the object
print(XR7ApiRoutersForensicCatalogConfirmRequest.to_json())

# convert the object into a dict
xr7_api_routers_forensic_catalog_confirm_request_dict = xr7_api_routers_forensic_catalog_confirm_request_instance.to_dict()
# create an instance of XR7ApiRoutersForensicCatalogConfirmRequest from a dict
xr7_api_routers_forensic_catalog_confirm_request_from_dict = XR7ApiRoutersForensicCatalogConfirmRequest.from_dict(xr7_api_routers_forensic_catalog_confirm_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
