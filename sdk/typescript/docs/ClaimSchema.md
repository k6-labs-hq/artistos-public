
# ClaimSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`anomalyId` | string
`claimType` | string
`status` | [ClaimStatus](ClaimStatus.md)
`recoveredAmount` | number
`currency` | string
`contingencyFee` | number
`evidence` | { [key: string]: any; }
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { ClaimSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "anomalyId": null,
  "claimType": null,
  "status": null,
  "recoveredAmount": null,
  "currency": null,
  "contingencyFee": null,
  "evidence": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies ClaimSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ClaimSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


