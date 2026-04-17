# ReferralRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**referred_artist_id** | **str** |  |

## Example

```python
from xr7_sdk.models.referral_request import ReferralRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ReferralRequest from a JSON string
referral_request_instance = ReferralRequest.from_json(json)
# print the JSON string representation of the object
print(ReferralRequest.to_json())

# convert the object into a dict
referral_request_dict = referral_request_instance.to_dict()
# create an instance of ReferralRequest from a dict
referral_request_from_dict = ReferralRequest.from_dict(referral_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
