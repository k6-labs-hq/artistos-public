# RoyaltyLedgerEntryCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source** | **str** |  | 
**record_type** | [**LedgerRecordType**](LedgerRecordType.md) |  | 
**source_file** | **str** |  | [optional] 
**source_row** | **int** |  | [optional] 
**contract_version** | **str** |  | [optional] 
**work_id** | **str** |  | [optional] 
**event_type** | **str** |  | [optional] 
**period_start** | **date** |  | [optional] 
**period_end** | **date** |  | [optional] 
**quantity** | **float** |  | [optional] [default to 0.0]
**rate** | **float** |  | [optional] [default to 0.0]
**expected_amount** | **float** |  | [optional] [default to 0.0]
**received_amount** | **float** |  | [optional] [default to 0.0]
**currency** | **str** |  | [optional] [default to 'USD']
**fx_rate_used** | **float** |  | [optional] 
**territory** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.royalty_ledger_entry_create import RoyaltyLedgerEntryCreate

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of RoyaltyLedgerEntryCreate from a JSON string
royalty_ledger_entry_create_instance = RoyaltyLedgerEntryCreate.from_json(json)
# print the JSON string representation of the object
print(RoyaltyLedgerEntryCreate.to_json())

# convert the object into a dict
royalty_ledger_entry_create_dict = royalty_ledger_entry_create_instance.to_dict()
# create an instance of RoyaltyLedgerEntryCreate from a dict
royalty_ledger_entry_create_from_dict = RoyaltyLedgerEntryCreate.from_dict(royalty_ledger_entry_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


