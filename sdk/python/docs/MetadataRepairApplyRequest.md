# MetadataRepairApplyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tenant_id** | **str** |  | [optional] [default to 'default']
**suggestion_ids** | **List[str]** |  | [optional] 
**dry_run** | **bool** |  | [optional] [default to False]

## Example

```python
from xr7_sdk.models.metadata_repair_apply_request import MetadataRepairApplyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MetadataRepairApplyRequest from a JSON string
metadata_repair_apply_request_instance = MetadataRepairApplyRequest.from_json(json)
# print the JSON string representation of the object
print(MetadataRepairApplyRequest.to_json())

# convert the object into a dict
metadata_repair_apply_request_dict = metadata_repair_apply_request_instance.to_dict()
# create an instance of MetadataRepairApplyRequest from a dict
metadata_repair_apply_request_from_dict = MetadataRepairApplyRequest.from_dict(metadata_repair_apply_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


