# WidgetLeadSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  |
**artist_name** | **str** |  |
**email** | **str** |  |
**career_stage** | **str** |  |
**genre** | **str** |  |
**years_active** | **int** |  |
**territory** | **str** |  |
**estimate_conservative** | **float** |  |
**estimate_likely** | **float** |  |
**estimate_optimistic** | **float** |  |
**currency** | **str** |  |
**results_emailed** | **bool** |  |
**claimed** | **bool** |  |
**claim_submitted_at** | **datetime** |  |
**created_at** | **datetime** |  |

## Example

```python
from xr7_sdk.models.widget_lead_schema import WidgetLeadSchema

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetLeadSchema from a JSON string
widget_lead_schema_instance = WidgetLeadSchema.from_json(json)
# print the JSON string representation of the object
print(WidgetLeadSchema.to_json())

# convert the object into a dict
widget_lead_schema_dict = widget_lead_schema_instance.to_dict()
# create an instance of WidgetLeadSchema from a dict
widget_lead_schema_from_dict = WidgetLeadSchema.from_dict(widget_lead_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
