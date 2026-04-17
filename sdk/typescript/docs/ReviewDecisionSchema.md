
# ReviewDecisionSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`reviewItemId` | string
`analystEmail` | string
`decision` | [ReviewDecisionType](ReviewDecisionType.md)
`notes` | string
`createdAt` | Date

## Example

```typescript
import type { ReviewDecisionSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "reviewItemId": null,
  "analystEmail": null,
  "decision": null,
  "notes": null,
  "createdAt": null,
} satisfies ReviewDecisionSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ReviewDecisionSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
