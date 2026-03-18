# TVFilmBulkClaimDraftRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anomaly_ids** | **List[str]** |  | [optional] 
**group_by_template** | **bool** |  | [optional] [default to True]

## Example

```python
from xr7_sdk.models.tv_film_bulk_claim_draft_request import TVFilmBulkClaimDraftRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TVFilmBulkClaimDraftRequest from a JSON string
tv_film_bulk_claim_draft_request_instance = TVFilmBulkClaimDraftRequest.from_json(json)
# print the JSON string representation of the object
print(TVFilmBulkClaimDraftRequest.to_json())

# convert the object into a dict
tv_film_bulk_claim_draft_request_dict = tv_film_bulk_claim_draft_request_instance.to_dict()
# create an instance of TVFilmBulkClaimDraftRequest from a dict
tv_film_bulk_claim_draft_request_from_dict = TVFilmBulkClaimDraftRequest.from_dict(tv_film_bulk_claim_draft_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


