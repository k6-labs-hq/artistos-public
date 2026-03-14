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
**evidence** | **Dict[str, object]** |  | [optional] 
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


