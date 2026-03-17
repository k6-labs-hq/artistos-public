# OptimizationSimulationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**changes** | **Dict[str, object]** |  | 

## Example

```python
from xr7_sdk.models.optimization_simulation_request import OptimizationSimulationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of OptimizationSimulationRequest from a JSON string
optimization_simulation_request_instance = OptimizationSimulationRequest.from_json(json)
# print the JSON string representation of the object
print(OptimizationSimulationRequest.to_json())

# convert the object into a dict
optimization_simulation_request_dict = optimization_simulation_request_instance.to_dict()
# create an instance of OptimizationSimulationRequest from a dict
optimization_simulation_request_from_dict = OptimizationSimulationRequest.from_dict(optimization_simulation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


