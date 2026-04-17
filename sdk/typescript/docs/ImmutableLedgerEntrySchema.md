
# ImmutableLedgerEntrySchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`entryType` | string
`payloadJson` | string
`priorHash` | string
`entryHash` | string
`createdAt` | Date

## Example

```typescript
import type { ImmutableLedgerEntrySchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "entryType": null,
  "payloadJson": null,
  "priorHash": null,
  "entryHash": null,
  "createdAt": null,
} satisfies ImmutableLedgerEntrySchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ImmutableLedgerEntrySchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
