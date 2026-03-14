
# EvidenceAnchorSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`claimId` | string
`packetHash` | string
`chainHash` | string
`anchorProvider` | string
`anchorReference` | string
`createdAt` | Date

## Example

```typescript
import type { EvidenceAnchorSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "claimId": null,
  "packetHash": null,
  "chainHash": null,
  "anchorProvider": null,
  "anchorReference": null,
  "createdAt": null,
} satisfies EvidenceAnchorSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EvidenceAnchorSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


