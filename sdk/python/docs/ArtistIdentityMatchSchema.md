# ArtistIdentityMatchSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**statement_id** | **str** |  | [optional] 
**confidence_score** | **float** |  | 
**confidence_band** | [**IdentityConfidenceBand**](IdentityConfidenceBand.md) |  | 
**decision_status** | [**IdentityDecisionStatus**](IdentityDecisionStatus.md) |  | 
**decision_reason** | **str** |  | [optional] 
**decision_actor** | **str** |  | [optional] 
**decision_at** | **datetime** |  | [optional] 
**matched_profile** | **Dict[str, object]** |  | 
**score_breakdown** | **Dict[str, object]** |  | 
**chain_hash** | **str** |  | 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.artist_identity_match_schema import ArtistIdentityMatchSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ArtistIdentityMatchSchema from a JSON string
artist_identity_match_schema_instance = ArtistIdentityMatchSchema.from_json(json)
# print the JSON string representation of the object
print(ArtistIdentityMatchSchema.to_json())

# convert the object into a dict
artist_identity_match_schema_dict = artist_identity_match_schema_instance.to_dict()
# create an instance of ArtistIdentityMatchSchema from a dict
artist_identity_match_schema_from_dict = ArtistIdentityMatchSchema.from_dict(artist_identity_match_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


