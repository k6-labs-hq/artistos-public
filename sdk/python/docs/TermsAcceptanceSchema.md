# TermsAcceptanceSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**terms_version** | **str** |  | 
**text_sha256** | **str** |  | 
**accepted_at** | **datetime** |  | 
**ip_address** | **str** |  | [optional] 
**user_agent** | **str** |  | [optional] 

## Example

```python
from xr7_sdk.models.terms_acceptance_schema import TermsAcceptanceSchema

# TODO update the JSON string below
json = "{}"
# create an instance of TermsAcceptanceSchema from a JSON string
terms_acceptance_schema_instance = TermsAcceptanceSchema.from_json(json)
# print the JSON string representation of the object
print(TermsAcceptanceSchema.to_json())

# convert the object into a dict
terms_acceptance_schema_dict = terms_acceptance_schema_instance.to_dict()
# create an instance of TermsAcceptanceSchema from a dict
terms_acceptance_schema_from_dict = TermsAcceptanceSchema.from_dict(terms_acceptance_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


