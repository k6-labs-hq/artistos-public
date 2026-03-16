# ClaimTemplateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subtype** | **str** |  | 
**counterparty_name** | **str** |  | 
**amount_claimed** | **float** |  | 
**evidence_summary** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.claim_template_request import ClaimTemplateRequest

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of ClaimTemplateRequest from a JSON string
claim_template_request_instance = ClaimTemplateRequest.from_json(json)
# print the JSON string representation of the object
print(ClaimTemplateRequest.to_json())

# convert the object into a dict
claim_template_request_dict = claim_template_request_instance.to_dict()
# create an instance of ClaimTemplateRequest from a dict
claim_template_request_from_dict = ClaimTemplateRequest.from_dict(claim_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


