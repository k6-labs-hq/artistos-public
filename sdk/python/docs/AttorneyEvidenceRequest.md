# AttorneyEvidenceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**additional_notes** | **str** |  | [optional]
**attorney_engagement_deadline** | **datetime** |  | [optional]

## Example

```python
from xr7_sdk.models.attorney_evidence_request import AttorneyEvidenceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AttorneyEvidenceRequest from a JSON string
attorney_evidence_request_instance = AttorneyEvidenceRequest.from_json(json)
# print the JSON string representation of the object
print(AttorneyEvidenceRequest.to_json())

# convert the object into a dict
attorney_evidence_request_dict = attorney_evidence_request_instance.to_dict()
# create an instance of AttorneyEvidenceRequest from a dict
attorney_evidence_request_from_dict = AttorneyEvidenceRequest.from_dict(attorney_evidence_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
