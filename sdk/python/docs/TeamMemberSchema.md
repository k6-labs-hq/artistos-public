# TeamMemberSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**artist_id** | **str** |  | 
**user_email** | **str** |  | 
**role** | [**TeamRole**](TeamRole.md) |  | 
**created_at** | **datetime** |  | 

## Example

```python
from xr7_sdk.models.team_member_schema import TeamMemberSchema

# Example JSON shown below; adjust for your use case
json = "{}"
# create an instance of TeamMemberSchema from a JSON string
team_member_schema_instance = TeamMemberSchema.from_json(json)
# print the JSON string representation of the object
print(TeamMemberSchema.to_json())

# convert the object into a dict
team_member_schema_dict = team_member_schema_instance.to_dict()
# create an instance of TeamMemberSchema from a dict
team_member_schema_from_dict = TeamMemberSchema.from_dict(team_member_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


