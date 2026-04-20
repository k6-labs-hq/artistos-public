# XR7ConnectorCredentialUpsert


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**provider** | **str** |  |
**external_account_id** | **str** |  |
**access_token** | **str** |  |
**refresh_token** | **str** |  | [optional]
**expires_in_seconds** | **int** |  | [optional]
**granted_scopes** | **List[str]** |  | [optional]
**tenant_id** | **str** |  | [optional] [default to 'default']

## Example

```python
from xr7_sdk.models.xr7_connector_credential_upsert import XR7ConnectorCredentialUpsert

# TODO update the JSON string below
json = "{}"
# create an instance of XR7ConnectorCredentialUpsert from a JSON string
xr7_connector_credential_upsert_instance = XR7ConnectorCredentialUpsert.from_json(json)
# print the JSON string representation of the object
print(XR7ConnectorCredentialUpsert.to_json())

# convert the object into a dict
xr7_connector_credential_upsert_dict = xr7_connector_credential_upsert_instance.to_dict()
# create an instance of XR7ConnectorCredentialUpsert from a dict
xr7_connector_credential_upsert_from_dict = XR7ConnectorCredentialUpsert.from_dict(xr7_connector_credential_upsert_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
