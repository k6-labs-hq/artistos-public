# ForensicUniversalRoyaltyEventCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**work_id** | **str** |  | [optional] 
**isrc** | **str** |  | [optional] 
**iswc** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**artist_name** | **str** |  | [optional] 
**writer_name** | **str** |  | [optional] 
**publisher_name** | **str** |  | [optional] 
**distributor** | **str** |  | [optional] 
**platform** | **str** |  | [optional] 
**usage_type** | **str** |  | [optional] 
**usage_count** | **int** |  | [optional] [default to 0]
**payout_amount** | **float** |  | [optional] [default to 0.0]
**payout_currency** | **str** |  | [optional] [default to 'USD']
**statement_period_start** | **date** |  | [optional] 
**statement_period_end** | **date** |  | [optional] 
**source_file_id** | **str** |  | [optional] 
**confidence_score** | **float** |  | [optional] [default to 0.0]
**metadata_flags** | **Dict[str, str]** |  | [optional] 

## Example

```python
from xr7_sdk.models.forensic_universal_royalty_event_create import ForensicUniversalRoyaltyEventCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ForensicUniversalRoyaltyEventCreate from a JSON string
forensic_universal_royalty_event_create_instance = ForensicUniversalRoyaltyEventCreate.from_json(json)
# print the JSON string representation of the object
print(ForensicUniversalRoyaltyEventCreate.to_json())

# convert the object into a dict
forensic_universal_royalty_event_create_dict = forensic_universal_royalty_event_create_instance.to_dict()
# create an instance of ForensicUniversalRoyaltyEventCreate from a dict
forensic_universal_royalty_event_create_from_dict = ForensicUniversalRoyaltyEventCreate.from_dict(forensic_universal_royalty_event_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


