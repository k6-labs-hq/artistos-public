
# BrandingProfileUpsertRequest


## Properties

Name | Type
------------ | -------------
`displayName` | string
`logoUrl` | string
`primaryColor` | string
`secondaryColor` | string
`accentColor` | string
`dashboardHeaderText` | string
`dashboardFooterText` | string
`supportEmail` | string
`supportPhone` | string
`legalDisclaimer` | string
`customDomain` | string
`whiteLabelEnabled` | boolean

## Example

```typescript
import type { BrandingProfileUpsertRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "displayName": null,
  "logoUrl": null,
  "primaryColor": null,
  "secondaryColor": null,
  "accentColor": null,
  "dashboardHeaderText": null,
  "dashboardFooterText": null,
  "supportEmail": null,
  "supportPhone": null,
  "legalDisclaimer": null,
  "customDomain": null,
  "whiteLabelEnabled": null,
} satisfies BrandingProfileUpsertRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BrandingProfileUpsertRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


