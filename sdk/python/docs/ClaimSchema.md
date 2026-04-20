# ClaimSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  |
**artist_id** | **str** |  |
**anomaly_id** | **str** |  |
**claim_type** | **str** |  |
**status** | [**ClaimStatus**](ClaimStatus.md) |  |
**recovered_amount** | **float** |  | [optional]
**currency** | **str** |  |
**contingency_fee** | **float** |  | [optional]
**platform_fee_percent** | **float** |  | [optional] [default to 12.0]
**platform_fee_amount** | **float** |  | [optional]
**artist_net_amount** | **float** |  | [optional]
**remittance_method** | **str** |  | [optional]
**remittance_reference_number** | **str** |  | [optional]
**remittance_received_at** | **datetime** |  | [optional]
**trolley_payment_id** | **str** |  | [optional]
**trolley_payment_status** | **str** |  | [optional]
**trolley_fx_rate** | **float** |  | [optional]
**trolley_local_amount** | **float** |  | [optional]
**trolley_local_currency** | **str** |  | [optional]
**payout_retry_count** | **int** |  | [optional] [default to 0]
**payout_failure_reason** | **str** |  | [optional]
**evidence** | **Dict[str, object]** |  | [optional]
**payer_name** | **str** |  | [optional]
**payer_contact** | **str** |  | [optional]
**original_due_date** | **datetime** |  | [optional]
**proof_submitted_at** | **datetime** |  | [optional]
**grace_period_days** | **int** |  | [optional] [default to 60]
**sol_deadline** | **datetime** |  | [optional]
**governing_law_state** | **str** |  | [optional] [default to 'USA']
**contract_type** | **str** |  | [optional] [default to 'recording']
**infringement_date** | **datetime** |  | [optional]
**discovery_date** | **datetime** |  | [optional]
**sol_window_years** | **int** |  | [optional]
**sol_citation_source** | **str** |  | [optional]
**communications** | **List[Dict[str, object]]** |  | [optional]
**anomaly_report** | **Dict[str, object]** |  | [optional]
**supporting_documents** | **List[Dict[str, object]]** |  | [optional]
**attorney_file_generated** | **bool** |  | [optional] [default to False]
**attorney_file_generated_at** | **datetime** |  | [optional]
**created_at** | **datetime** |  |
**updated_at** | **datetime** |  |

## Example

```python
from xr7_sdk.models.claim_schema import ClaimSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ClaimSchema from a JSON string
claim_schema_instance = ClaimSchema.from_json(json)
# print the JSON string representation of the object
print(ClaimSchema.to_json())

# convert the object into a dict
claim_schema_dict = claim_schema_instance.to_dict()
# create an instance of ClaimSchema from a dict
claim_schema_from_dict = ClaimSchema.from_dict(claim_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
