# StructuredFeedbackRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anomaly_id** | **str** |  | [optional] 
**claim_id** | **str** |  | [optional] 
**outcome** | **str** |  | [optional] 
**recovered_amount** | **float** |  | [optional] 
**reason_code** | **str** |  | [optional] 
**analyst_note** | **str** |  | [optional] 
**feedback_type** | [**MLFeedbackType**](MLFeedbackType.md) |  | [optional] 
**source_type** | **str** |  | [optional] 
**source_id** | **str** |  | [optional] 
**subtype** | **str** |  | [optional] 
**category** | **str** |  | [optional] 
**artist_profile_segment** | **str** |  | [optional] 
**model_version** | **str** |  | [optional] 
**model_prediction** | **float** |  | [optional] 
**human_decision** | **str** |  | [optional] 
**estimated_amount** | **float** |  | [optional] 
**actual_amount** | **float** |  | [optional] 
**payload** | **Dict[str, object]** |  | [optional] 

## Example

```python
from xr7_sdk.models.structured_feedback_request import StructuredFeedbackRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StructuredFeedbackRequest from a JSON string
structured_feedback_request_instance = StructuredFeedbackRequest.from_json(json)
# print the JSON string representation of the object
print(StructuredFeedbackRequest.to_json())

# convert the object into a dict
structured_feedback_request_dict = structured_feedback_request_instance.to_dict()
# create an instance of StructuredFeedbackRequest from a dict
structured_feedback_request_from_dict = StructuredFeedbackRequest.from_dict(structured_feedback_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


