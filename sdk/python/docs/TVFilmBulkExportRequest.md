# TVFilmBulkExportRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**claim_ids** | **List[str]** |  | [optional] 

## Example

```python
from xr7_sdk.models.tv_film_bulk_export_request import TVFilmBulkExportRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TVFilmBulkExportRequest from a JSON string
tv_film_bulk_export_request_instance = TVFilmBulkExportRequest.from_json(json)
# print the JSON string representation of the object
print(TVFilmBulkExportRequest.to_json())

# convert the object into a dict
tv_film_bulk_export_request_dict = tv_film_bulk_export_request_instance.to_dict()
# create an instance of TVFilmBulkExportRequest from a dict
tv_film_bulk_export_request_from_dict = TVFilmBulkExportRequest.from_dict(tv_film_bulk_export_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


