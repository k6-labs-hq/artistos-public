
# SupportActionResponse


## Properties

Name | Type
------------ | -------------
`artistId` | string
`action` | string
`result` | { [key: string]: any; }
`formattedMessage` | string

## Example

```typescript
import type { SupportActionResponse } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "artistId": null,
  "action": null,
  "result": null,
  "formattedMessage": null,
} satisfies SupportActionResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SupportActionResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


