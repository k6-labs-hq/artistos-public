# PreSignatureContractReviewRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contract_text** | **str** |  | 

## Example

```python
from xr7_sdk.models.pre_signature_contract_review_request import PreSignatureContractReviewRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PreSignatureContractReviewRequest from a JSON string
pre_signature_contract_review_request_instance = PreSignatureContractReviewRequest.from_json(json)
# print the JSON string representation of the object
print(PreSignatureContractReviewRequest.to_json())

# convert the object into a dict
pre_signature_contract_review_request_dict = pre_signature_contract_review_request_instance.to_dict()
# create an instance of PreSignatureContractReviewRequest from a dict
pre_signature_contract_review_request_from_dict = PreSignatureContractReviewRequest.from_dict(pre_signature_contract_review_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


