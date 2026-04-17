# TVFilmTrustExplainRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | **str** |  |
**agency_mode** | **bool** |  | [optional] [default to False]

## Example

```python
from xr7_sdk.models.tv_film_trust_explain_request import TVFilmTrustExplainRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TVFilmTrustExplainRequest from a JSON string
tv_film_trust_explain_request_instance = TVFilmTrustExplainRequest.from_json(json)
# print the JSON string representation of the object
print(TVFilmTrustExplainRequest.to_json())

# convert the object into a dict
tv_film_trust_explain_request_dict = tv_film_trust_explain_request_instance.to_dict()
# create an instance of TVFilmTrustExplainRequest from a dict
tv_film_trust_explain_request_from_dict = TVFilmTrustExplainRequest.from_dict(tv_film_trust_explain_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
