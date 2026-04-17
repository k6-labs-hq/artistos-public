
# ArtistIdentityMatchSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`statementId` | string
`confidenceScore` | number
`confidenceBand` | [IdentityConfidenceBand](IdentityConfidenceBand.md)
`decisionStatus` | [IdentityDecisionStatus](IdentityDecisionStatus.md)
`decisionReason` | string
`decisionActor` | string
`decisionAt` | Date
`matchedProfile` | { [key: string]: any; }
`scoreBreakdown` | { [key: string]: any; }
`chainHash` | string
`createdAt` | Date

## Example

```typescript
import type { ArtistIdentityMatchSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "statementId": null,
  "confidenceScore": null,
  "confidenceBand": null,
  "decisionStatus": null,
  "decisionReason": null,
  "decisionActor": null,
  "decisionAt": null,
  "matchedProfile": null,
  "scoreBreakdown": null,
  "chainHash": null,
  "createdAt": null,
} satisfies ArtistIdentityMatchSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ArtistIdentityMatchSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
