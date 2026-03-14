
# CeleroDisburseRequest

Disburse a net recovery amount to the artist via ACH.  ``amount`` is the net amount in USD after XR7\'s fee has been deducted. ``claim_id`` is optional — omit for manual / ad-hoc disbursements.

## Properties

Name | Type
------------ | -------------
`amount` | number
`currency` | string
`claimId` | string
`description` | string

## Example

```typescript
import type { CeleroDisburseRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "amount": null,
  "currency": null,
  "claimId": null,
  "description": null,
} satisfies CeleroDisburseRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CeleroDisburseRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


