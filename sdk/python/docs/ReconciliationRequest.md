# ReconciliationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tenant_id** | **str** |  | [optional] [default to 'default']
**min_auto_match** | **float** |  | [optional] [default to 0.92]
**queue_backend** | **str** |  | [optional] [default to 'celery']

## Example

```python
from xr7_sdk.models.reconciliation_request import ReconciliationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ReconciliationRequest from a JSON string
reconciliation_request_instance = ReconciliationRequest.from_json(json)
# print the JSON string representation of the object
print(ReconciliationRequest.to_json())

# convert the object into a dict
reconciliation_request_dict = reconciliation_request_instance.to_dict()
# create an instance of ReconciliationRequest from a dict
reconciliation_request_from_dict = ReconciliationRequest.from_dict(reconciliation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


