# TVFilmClaimDraftRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anomaly_ids** | **List[str]** |  | [optional] 
**union_template** | **str** |  | [optional] [default to 'SAG-AFTRA']

## Example

```python
from xr7_sdk.models.tv_film_claim_draft_request import TVFilmClaimDraftRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TVFilmClaimDraftRequest from a JSON string
tv_film_claim_draft_request_instance = TVFilmClaimDraftRequest.from_json(json)
# print the JSON string representation of the object
print(TVFilmClaimDraftRequest.to_json())

# convert the object into a dict
tv_film_claim_draft_request_dict = tv_film_claim_draft_request_instance.to_dict()
# create an instance of TVFilmClaimDraftRequest from a dict
tv_film_claim_draft_request_from_dict = TVFilmClaimDraftRequest.from_dict(tv_film_claim_draft_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


