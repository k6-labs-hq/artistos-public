# TeamMemberCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_email** | **str** |  | 
**role** | [**TeamRole**](TeamRole.md) |  | 

## Example

```python
from xr7_sdk.models.team_member_create import TeamMemberCreate

# TODO update the JSON string below
json = "{}"
# create an instance of TeamMemberCreate from a JSON string
team_member_create_instance = TeamMemberCreate.from_json(json)
# print the JSON string representation of the object
print(TeamMemberCreate.to_json())

# convert the object into a dict
team_member_create_dict = team_member_create_instance.to_dict()
# create an instance of TeamMemberCreate from a dict
team_member_create_from_dict = TeamMemberCreate.from_dict(team_member_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


