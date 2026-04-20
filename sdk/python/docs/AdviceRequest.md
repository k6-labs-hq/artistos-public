# AdviceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artist_dashboard** | **Dict[str, object]** |  | [optional]
**user_message** | **str** |  | [optional]

## Example

```python
from xr7_sdk.models.advice_request import AdviceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AdviceRequest from a JSON string
advice_request_instance = AdviceRequest.from_json(json)
# print the JSON string representation of the object
print(AdviceRequest.to_json())

# convert the object into a dict
advice_request_dict = advice_request_instance.to_dict()
# create an instance of AdviceRequest from a dict
advice_request_from_dict = AdviceRequest.from_dict(advice_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
