# WeeklyStoryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_recovered** | **float** |  | [optional] [default to 0.0]
**total_recoverable** | **float** |  | [optional] [default to 0.0]
**new_anomalies** | **int** |  | [optional] [default to 0]
**claims_progressed** | **int** |  | [optional] [default to 0]
**deposits** | **List[Dict[str, object]]** |  | [optional] [default to []]
**currency** | **str** |  | [optional] [default to 'USD']

## Example

```python
from xr7_sdk.models.weekly_story_request import WeeklyStoryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WeeklyStoryRequest from a JSON string
weekly_story_request_instance = WeeklyStoryRequest.from_json(json)
# print the JSON string representation of the object
print(WeeklyStoryRequest.to_json())

# convert the object into a dict
weekly_story_request_dict = weekly_story_request_instance.to_dict()
# create an instance of WeeklyStoryRequest from a dict
weekly_story_request_from_dict = WeeklyStoryRequest.from_dict(weekly_story_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
