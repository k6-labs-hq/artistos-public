# ContractExtractRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contract_id** | **str** |  | [optional] 
**contract_text** | **str** |  | 
**effective_start** | **date** |  | [optional] 
**effective_end** | **date** |  | [optional] 
**extracted_from** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.contract_extract_request import ContractExtractRequest

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of ContractExtractRequest from a JSON string
contract_extract_request_instance = ContractExtractRequest.from_json(json)
# print the JSON string representation of the object
print(ContractExtractRequest.to_json())

# convert the object into a dict
contract_extract_request_dict = contract_extract_request_instance.to_dict()
# create an instance of ContractExtractRequest from a dict
contract_extract_request_from_dict = ContractExtractRequest.from_dict(contract_extract_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


