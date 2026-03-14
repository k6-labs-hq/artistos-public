
# CeleroRegisterRequest

Information needed to create an artist as a Celero customer.  Card / bank account details are collected separately via Celero\'s hosted Collect.js form and never pass through XR7 servers.

## Properties

Name | Type
------------ | -------------
`firstName` | string
`lastName` | string
`email` | string
`company` | string
`address1` | string
`city` | string
`state` | string
`zipCode` | string
`country` | string
`phone` | string

## Example

```typescript
import type { CeleroRegisterRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "firstName": null,
  "lastName": null,
  "email": null,
  "company": null,
  "address1": null,
  "city": null,
  "state": null,
  "zipCode": null,
  "country": null,
  "phone": null,
} satisfies CeleroRegisterRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CeleroRegisterRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


