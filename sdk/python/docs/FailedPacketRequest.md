# FailedPacketRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**failure_reason** | **str** |  |

## Example

```python
from xr7_sdk.models.failed_packet_request import FailedPacketRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FailedPacketRequest from a JSON string
failed_packet_request_instance = FailedPacketRequest.from_json(json)
# print the JSON string representation of the object
print(FailedPacketRequest.to_json())

# convert the object into a dict
failed_packet_request_dict = failed_packet_request_instance.to_dict()
# create an instance of FailedPacketRequest from a dict
failed_packet_request_from_dict = FailedPacketRequest.from_dict(failed_packet_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
