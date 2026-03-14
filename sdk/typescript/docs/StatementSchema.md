
# StatementSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`filename` | string
`fileHash` | string
`formatDetected` | string
`rowCount` | number
`eventsCreated` | number
`paymentsCreated` | number
`skippedRows` | number
`status` | string
`errorSummary` | string
`uploadedAt` | Date

## Example

```typescript
import type { StatementSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "filename": null,
  "fileHash": null,
  "formatDetected": null,
  "rowCount": null,
  "eventsCreated": null,
  "paymentsCreated": null,
  "skippedRows": null,
  "status": null,
  "errorSummary": null,
  "uploadedAt": null,
} satisfies StatementSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StatementSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


