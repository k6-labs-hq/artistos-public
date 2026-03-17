# TermsAcceptRequest

Body for POST /artists/{artist_id}/terms/accept.  ``terms_version`` must match the version the server returns from GET /terms.  This prevents a client that cached an old version of the T&C from accidentally accepting stale terms.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**terms_version** | **str** |  | 
**agreed** | **bool** |  | 

## Example

```python
from xr7_sdk.models.terms_accept_request import TermsAcceptRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TermsAcceptRequest from a JSON string
terms_accept_request_instance = TermsAcceptRequest.from_json(json)
# print the JSON string representation of the object
print(TermsAcceptRequest.to_json())

# convert the object into a dict
terms_accept_request_dict = terms_accept_request_instance.to_dict()
# create an instance of TermsAcceptRequest from a dict
terms_accept_request_from_dict = TermsAcceptRequest.from_dict(terms_accept_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


