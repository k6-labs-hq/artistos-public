# ReconcileRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**recovered_amount** | **float** |  |
**currency** | **str** |  |

## Example

```python
from xr7_sdk.models.reconcile_request import ReconcileRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ReconcileRequest from a JSON string
reconcile_request_instance = ReconcileRequest.from_json(json)
# print the JSON string representation of the object
print(ReconcileRequest.to_json())

# convert the object into a dict
reconcile_request_dict = reconcile_request_instance.to_dict()
# create an instance of ReconcileRequest from a dict
reconcile_request_from_dict = ReconcileRequest.from_dict(reconcile_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
