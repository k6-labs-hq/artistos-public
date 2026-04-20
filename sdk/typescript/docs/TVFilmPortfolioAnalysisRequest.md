
# TVFilmPortfolioAnalysisRequest


## Properties

Name | Type
------------ | -------------
`organizationName` | string
`entityType` | string
`records` | Array&lt;{ [key: string]: any; }&gt;
`uploadedFilename` | string

## Example

```typescript
import type { TVFilmPortfolioAnalysisRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "organizationName": null,
  "entityType": null,
  "records": null,
  "uploadedFilename": null,
} satisfies TVFilmPortfolioAnalysisRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TVFilmPortfolioAnalysisRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
