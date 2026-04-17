# ArtistSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  |
**name** | **str** |  |
**email** | **str** |  | [optional]
**role** | **str** |  | [optional]
**ipi_number** | **str** |  | [optional]
**stage_names** | **List[str]** |  | [optional]
**created_at** | **datetime** |  |
**status** | [**ArtistLifecycleStatus**](ArtistLifecycleStatus.md) |  |
**onboarded_at** | **datetime** |  | [optional]
**activated_at** | **datetime** |  | [optional]
**first_name** | **str** |  | [optional]
**last_name** | **str** |  | [optional]
**country_code** | **str** |  | [optional] [default to 'US']
**trolley_recipient_id** | **str** |  | [optional]
**payout_account_status** | **str** |  | [optional] [default to 'not_started']
**payout_method_type** | **str** |  | [optional]
**payout_last4** | **str** |  | [optional]
**tax_form_status** | **str** |  | [optional] [default to 'pending']
**default_attorney_grace_period_days** | **int** |  | [optional] [default to 60]
**primary_jurisdiction** | **str** |  | [optional] [default to 'USA']
**preferred_contract_type** | **str** |  | [optional] [default to 'recording']
**xr7_future_leakage_prevented** | **float** |  | [optional] [default to 0.0]
**is_founder** | **bool** |  | [optional] [default to False]
**founder_slot_number** | **int** |  | [optional]
**founder_locked_at** | **datetime** |  | [optional]
**contingency_fee_percent** | **float** |  | [optional]
**primary_vertical** | **str** |  | [optional]
**tvfilm_role** | **str** |  | [optional]
**organization_type** | **str** |  | [optional]
**enterprise_mode_enabled** | **bool** |  | [optional] [default to False]

## Example

```python
from xr7_sdk.models.artist_schema import ArtistSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ArtistSchema from a JSON string
artist_schema_instance = ArtistSchema.from_json(json)
# print the JSON string representation of the object
print(ArtistSchema.to_json())

# convert the object into a dict
artist_schema_dict = artist_schema_instance.to_dict()
# create an instance of ArtistSchema from a dict
artist_schema_from_dict = ArtistSchema.from_dict(artist_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
