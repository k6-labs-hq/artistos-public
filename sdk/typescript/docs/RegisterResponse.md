
# RegisterResponse


## Properties

Name | Type
------------ | -------------
`sessionId` | string
`message` | string
`expiresInSeconds` | number
`devPhoneOtp` | string
`devEmailOtp` | string

## Example

```typescript
import type { RegisterResponse } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "sessionId": null,
  "message": null,
  "expiresInSeconds": null,
  "devPhoneOtp": null,
  "devEmailOtp": null,
} satisfies RegisterResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RegisterResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
