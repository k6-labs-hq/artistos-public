# ManualRemittanceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gross_amount** | **float** |  |
**remittance_method** | **str** |  |
**received_date** | **datetime** |  |
**reference_number** | **str** |  |

## Example

```python
from xr7_sdk.models.manual_remittance_request import ManualRemittanceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ManualRemittanceRequest from a JSON string
manual_remittance_request_instance = ManualRemittanceRequest.from_json(json)
# print the JSON string representation of the object
print(ManualRemittanceRequest.to_json())

# convert the object into a dict
manual_remittance_request_dict = manual_remittance_request_instance.to_dict()
# create an instance of ManualRemittanceRequest from a dict
manual_remittance_request_from_dict = ManualRemittanceRequest.from_dict(manual_remittance_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
