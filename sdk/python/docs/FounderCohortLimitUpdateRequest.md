# FounderCohortLimitUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**founder_cohort_limit** | **int** |  |

## Example

```python
from xr7_sdk.models.founder_cohort_limit_update_request import FounderCohortLimitUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FounderCohortLimitUpdateRequest from a JSON string
founder_cohort_limit_update_request_instance = FounderCohortLimitUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(FounderCohortLimitUpdateRequest.to_json())

# convert the object into a dict
founder_cohort_limit_update_request_dict = founder_cohort_limit_update_request_instance.to_dict()
# create an instance of FounderCohortLimitUpdateRequest from a dict
founder_cohort_limit_update_request_from_dict = FounderCohortLimitUpdateRequest.from_dict(founder_cohort_limit_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
