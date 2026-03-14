# ImmutableLedgerEntrySchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**entry_type** | **str** |  | 
**payload_json** | **str** |  | 
**prior_hash** | **str** |  | 
**entry_hash** | **str** |  | 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.immutable_ledger_entry_schema import ImmutableLedgerEntrySchema

# TODO update the JSON string below
json = "{}"
# create an instance of ImmutableLedgerEntrySchema from a JSON string
immutable_ledger_entry_schema_instance = ImmutableLedgerEntrySchema.from_json(json)
# print the JSON string representation of the object
print(ImmutableLedgerEntrySchema.to_json())

# convert the object into a dict
immutable_ledger_entry_schema_dict = immutable_ledger_entry_schema_instance.to_dict()
# create an instance of ImmutableLedgerEntrySchema from a dict
immutable_ledger_entry_schema_from_dict = ImmutableLedgerEntrySchema.from_dict(immutable_ledger_entry_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


