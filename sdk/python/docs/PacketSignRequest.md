# PacketSignRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**note** | **str** |  | [optional]

## Example

```python
from xr7_sdk.models.packet_sign_request import PacketSignRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PacketSignRequest from a JSON string
packet_sign_request_instance = PacketSignRequest.from_json(json)
# print the JSON string representation of the object
print(PacketSignRequest.to_json())

# convert the object into a dict
packet_sign_request_dict = packet_sign_request_instance.to_dict()
# create an instance of PacketSignRequest from a dict
packet_sign_request_from_dict = PacketSignRequest.from_dict(packet_sign_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
