# CeleroTransactionSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**claim_id** | **str** |  | 
**type** | [**CeleroTxnType**](CeleroTxnType.md) |  | 
**amount** | **float** |  | 
**currency** | **str** |  | 
**status** | [**CeleroTxnStatus**](CeleroTxnStatus.md) |  | 
**celero_transaction_id** | **str** |  | 
**celero_customer_vault_id** | **str** |  | 
**celero_auth_code** | **str** |  | 
**celero_response_code** | **str** |  | 
**celero_response_text** | **str** |  | 
**order_id** | **str** |  | 
**description** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.celero_transaction_schema import CeleroTransactionSchema

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of CeleroTransactionSchema from a JSON string
celero_transaction_schema_instance = CeleroTransactionSchema.from_json(json)
# print the JSON string representation of the object
print(CeleroTransactionSchema.to_json())

# convert the object into a dict
celero_transaction_schema_dict = celero_transaction_schema_instance.to_dict()
# create an instance of CeleroTransactionSchema from a dict
celero_transaction_schema_from_dict = CeleroTransactionSchema.from_dict(celero_transaction_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


