
# TermsAcceptanceSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`termsVersion` | string
`textSha256` | string
`acceptedAt` | Date
`ipAddress` | string
`userAgent` | string

## Example

```typescript
import type { TermsAcceptanceSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "termsVersion": null,
  "textSha256": null,
  "acceptedAt": null,
  "ipAddress": null,
  "userAgent": null,
} satisfies TermsAcceptanceSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TermsAcceptanceSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


