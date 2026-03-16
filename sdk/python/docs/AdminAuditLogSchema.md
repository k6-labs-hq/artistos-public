# AdminAuditLogSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**actor** | **str** |  | 
**action** | **str** |  | 
**resource_type** | **str** |  | 
**resource_id** | **str** |  | [optional] 
**details** | **Dict[str, object]** |  | [optional] 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.admin_audit_log_schema import AdminAuditLogSchema

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of AdminAuditLogSchema from a JSON string
admin_audit_log_schema_instance = AdminAuditLogSchema.from_json(json)
# print the JSON string representation of the object
print(AdminAuditLogSchema.to_json())

# convert the object into a dict
admin_audit_log_schema_dict = admin_audit_log_schema_instance.to_dict()
# create an instance of AdminAuditLogSchema from a dict
admin_audit_log_schema_from_dict = AdminAuditLogSchema.from_dict(admin_audit_log_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


