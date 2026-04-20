# TVFilmPortfolioAnalysisRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_name** | **str** |  |
**entity_type** | **str** |  |
**records** | **List[Dict[str, object]]** |  |
**uploaded_filename** | **str** |  | [optional]

## Example

```python
from xr7_sdk.models.tv_film_portfolio_analysis_request import TVFilmPortfolioAnalysisRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TVFilmPortfolioAnalysisRequest from a JSON string
tv_film_portfolio_analysis_request_instance = TVFilmPortfolioAnalysisRequest.from_json(json)
# print the JSON string representation of the object
print(TVFilmPortfolioAnalysisRequest.to_json())

# convert the object into a dict
tv_film_portfolio_analysis_request_dict = tv_film_portfolio_analysis_request_instance.to_dict()
# create an instance of TVFilmPortfolioAnalysisRequest from a dict
tv_film_portfolio_analysis_request_from_dict = TVFilmPortfolioAnalysisRequest.from_dict(tv_film_portfolio_analysis_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
