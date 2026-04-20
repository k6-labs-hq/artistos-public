
# SupportMessageView


## Properties

Name | Type
------------ | -------------
`id` | string
`threadId` | string
`role` | string
`message` | string
`confidence` | number
`metadata` | { [key: string]: any; }
`createdAt` | string

## Example

```typescript
import type { SupportMessageView } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "threadId": null,
  "role": null,
  "message": null,
  "confidence": null,
  "metadata": null,
  "createdAt": null,
} satisfies SupportMessageView

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SupportMessageView
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
