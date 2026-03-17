# EvidenceAnchorSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**claim_id** | **str** |  | 
**packet_hash** | **str** |  | 
**chain_hash** | **str** |  | 
**anchor_provider** | **str** |  | 
**anchor_reference** | **str** |  | 
**cid** | **str** |  | [optional] 
**tx_hash** | **str** |  | [optional] 
**blockchain_status** | **str** |  | 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.evidence_anchor_schema import EvidenceAnchorSchema

# TODO update the JSON string below
json = "{}"
# create an instance of EvidenceAnchorSchema from a JSON string
evidence_anchor_schema_instance = EvidenceAnchorSchema.from_json(json)
# print the JSON string representation of the object
print(EvidenceAnchorSchema.to_json())

# convert the object into a dict
evidence_anchor_schema_dict = evidence_anchor_schema_instance.to_dict()
# create an instance of EvidenceAnchorSchema from a dict
evidence_anchor_schema_from_dict = EvidenceAnchorSchema.from_dict(evidence_anchor_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


