# AnomalySchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**category** | [**AnomalyCategory**](AnomalyCategory.md) |  | 
**subtype** | **str** |  | 
**severity** | [**AnomalySeverity**](AnomalySeverity.md) |  | 
**expected_amount** | **float** |  | [optional] 
**actual_amount** | **float** |  | [optional] 
**estimated_recoverable** | **float** |  | [optional] 
**confidence_score** | **float** |  | 
**time_window_start** | **datetime** |  | [optional] 
**time_window_end** | **datetime** |  | [optional] 
**territory** | **str** |  | [optional] 
**status** | [**AnomalyStatus**](AnomalyStatus.md) |  | 
**description** | **str** |  | [optional] 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.anomaly_schema import AnomalySchema

# TODO update the JSON string below
json = "{}"
# create an instance of AnomalySchema from a JSON string
anomaly_schema_instance = AnomalySchema.from_json(json)
# print the JSON string representation of the object
print(AnomalySchema.to_json())

# convert the object into a dict
anomaly_schema_dict = anomaly_schema_instance.to_dict()
# create an instance of AnomalySchema from a dict
anomaly_schema_from_dict = AnomalySchema.from_dict(anomaly_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


