# LedgerIngestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entries** | [**List[RoyaltyLedgerEntryCreate]**](RoyaltyLedgerEntryCreate.md) |  |

## Example

```python
from xr7_sdk.models.ledger_ingest_request import LedgerIngestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LedgerIngestRequest from a JSON string
ledger_ingest_request_instance = LedgerIngestRequest.from_json(json)
# print the JSON string representation of the object
print(LedgerIngestRequest.to_json())

# convert the object into a dict
ledger_ingest_request_dict = ledger_ingest_request_instance.to_dict()
# create an instance of LedgerIngestRequest from a dict
ledger_ingest_request_from_dict = LedgerIngestRequest.from_dict(ledger_ingest_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
