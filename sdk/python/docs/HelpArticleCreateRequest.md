# HelpArticleCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  |
**body** | **str** |  |
**category** | **str** |  | [optional] [default to 'faq']

## Example

```python
from xr7_sdk.models.help_article_create_request import HelpArticleCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of HelpArticleCreateRequest from a JSON string
help_article_create_request_instance = HelpArticleCreateRequest.from_json(json)
# print the JSON string representation of the object
print(HelpArticleCreateRequest.to_json())

# convert the object into a dict
help_article_create_request_dict = help_article_create_request_instance.to_dict()
# create an instance of HelpArticleCreateRequest from a dict
help_article_create_request_from_dict = HelpArticleCreateRequest.from_dict(help_article_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
