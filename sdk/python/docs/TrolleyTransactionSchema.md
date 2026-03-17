# TrolleyTransactionSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**claim_id** | **str** |  | 
**type** | [**TrolleyTxnType**](TrolleyTxnType.md) |  | 
**status** | [**TrolleyTxnStatus**](TrolleyTxnStatus.md) |  | 
**gross_amount** | **float** |  | [optional] 
**platform_fee_amount** | **float** |  | [optional] 
**net_amount** | **float** |  | [optional] 
**source_currency** | **str** |  | [optional] [default to 'USD']
**local_amount** | **float** |  | [optional] 
**local_currency** | **str** |  | [optional] 
**exchange_rate** | **float** |  | [optional] 
**trolley_payment_id** | **str** |  | [optional] 
**trolley_batch_id** | **str** |  | [optional] 
**external_id** | **str** |  | [optional] 
**failure_reason** | **str** |  | [optional] 
**retry_count** | **int** |  | [optional] [default to 0]
**description** | **str** |  | [optional] 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.trolley_transaction_schema import TrolleyTransactionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of TrolleyTransactionSchema from a JSON string
trolley_transaction_schema_instance = TrolleyTransactionSchema.from_json(json)
# print the JSON string representation of the object
print(TrolleyTransactionSchema.to_json())

# convert the object into a dict
trolley_transaction_schema_dict = trolley_transaction_schema_instance.to_dict()
# create an instance of TrolleyTransactionSchema from a dict
trolley_transaction_schema_from_dict = TrolleyTransactionSchema.from_dict(trolley_transaction_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


