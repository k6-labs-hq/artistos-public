#!/usr/bin/env python3
"""
Add realistic example values to OpenAPI schema components.

This script reads the OpenAPI spec and adds example values to all schema
properties based on their types and names, which will be used by SDK
documentation generators to create meaningful code examples.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def generate_example_value(prop_name: str, prop_schema: dict[str, Any]) -> Any:
    """
    Generate a realistic example value based on property name and schema.

    Args:
        prop_name: The property name (e.g., "email", "artist_id")
        prop_schema: The OpenAPI property schema

    Returns:
        An appropriate example value for documentation
    """
    prop_type = prop_schema.get("type")
    prop_format = prop_schema.get("format")

    # Handle enums first
    if "enum" in prop_schema and prop_schema["enum"]:
        return prop_schema["enum"][0]

    # String type
    if prop_type == "string":
        lower_name = prop_name.lower()

        # Date/time formats
        if prop_format == "date-time" or "timestamp" in lower_name or "created_at" in lower_name or "updated_at" in lower_name:
            return "2026-04-16T10:30:00Z"
        if prop_format == "date":
            return "2026-04-16"
        if prop_format == "time":
            return "10:30:00"

        # Common field patterns
        if "email" in lower_name:
            return "artist@example.com"
        if "password" in lower_name:
            return "********"
        if "token" in lower_name or "key" in lower_name or "secret" in lower_name:
            return "sk_example_1234567890abcdef"
        if "url" in lower_name or "uri" in lower_name:
            return "https://example.com/resource"
        if "phone" in lower_name:
            return "+1-555-123-4567"
        if "artist_id" in lower_name:
            return "art_2a1b3c4d5e6f"
        if "claim_id" in lower_name:
            return "clm_9z8y7x6w5v4u"
        if "transaction_id" in lower_name:
            return "txn_5v4u3t2s1r0q"
        if "user_id" in lower_name:
            return "usr_1a2b3c4d5e6f"
        if "_id" in lower_name and lower_name.endswith("_id"):
            prefix = lower_name.replace("_id", "")[:3]
            return f"{prefix}_1a2b3c4d5e6f"
        if "name" in lower_name:
            return "Example Name"
        if "title" in lower_name:
            return "Example Title"
        if "description" in lower_name or "detail" in lower_name:
            return "This is an example description"
        if "status" in lower_name:
            return "active"
        if "role" in lower_name:
            return "artist"
        if "currency" in lower_name:
            return "USD"
        if "country" in lower_name:
            return "US"
        if "language" in lower_name or "locale" in lower_name:
            return "en-US"
        if "address" in lower_name:
            return "123 Main St, Anytown, CA 12345"
        if "city" in lower_name:
            return "San Francisco"
        if "state" in lower_name or "province" in lower_name:
            return "CA"
        if "zip" in lower_name or "postal" in lower_name:
            return "94102"

        # Default string
        return "example_value"

    # Number types
    if prop_type in ("integer", "number"):
        lower_name = prop_name.lower()

        if "amount" in lower_name or "price" in lower_name or "revenue" in lower_name:
            return 1234.56 if prop_type == "number" else 1234
        if "count" in lower_name or "total" in lower_name:
            return 42
        if "percentage" in lower_name or "percent" in lower_name or "rate" in lower_name:
            return 0.85 if prop_type == "number" else 85
        if "year" in lower_name:
            return 2026
        if "month" in lower_name:
            return 4
        if "day" in lower_name:
            return 16
        if "limit" in lower_name or "max" in lower_name:
            return 100
        if "offset" in lower_name or "skip" in lower_name:
            return 0
        if "page" in lower_name:
            return 1

        # Default number
        return 42 if prop_type == "integer" else 42.0

    # Boolean
    if prop_type == "boolean":
        lower_name = prop_name.lower()
        if "is_" in lower_name or "has_" in lower_name or "enabled" in lower_name:
            return True
        return False

    # Array
    if prop_type == "array":
        items_schema = prop_schema.get("items", {})
        item_example = generate_example_value("item", items_schema)
        return [item_example]

    # Object
    if prop_type == "object":
        # For generic objects, return a simple example
        return {"key": "value"}

    # Default fallback
    return None


def add_examples_to_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Add example values to a schema object's properties.

    Args:
        schema: An OpenAPI schema object

    Returns:
        The schema with examples added
    """
    if "properties" not in schema:
        return schema

    example_obj = {}

    for prop_name, prop_schema in schema["properties"].items():
        # Skip if example already exists
        if "example" in prop_schema:
            example_obj[prop_name] = prop_schema["example"]
            continue

        # Generate and add example
        example_value = generate_example_value(prop_name, prop_schema)
        if example_value is not None:
            prop_schema["example"] = example_value
            example_obj[prop_name] = example_value

    # Add schema-level example
    if example_obj and "example" not in schema:
        schema["example"] = example_obj

    return schema


def add_examples_to_openapi_spec(spec_path: Path) -> None:
    """
    Add examples to all schemas in the OpenAPI specification.

    Args:
        spec_path: Path to the openapi.json file
    """
    print(f"Reading OpenAPI spec from {spec_path}...")
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    # Process all schema components
    schemas = spec.get("components", {}).get("schemas", {})
    if not schemas:
        print("No schemas found in OpenAPI spec.")
        return

    print(f"Processing {len(schemas)} schemas...")
    modified_count = 0

    for schema_name, schema in schemas.items():
        if "properties" in schema:
            original = json.dumps(schema)
            add_examples_to_schema(schema)
            if json.dumps(schema) != original:
                modified_count += 1
                print(f"  ✓ Added examples to {schema_name}")

    # Write back to file
    print(f"\nWriting updated spec to {spec_path}...")
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)

    print(f"✅ Done! Modified {modified_count} schemas with examples.")


def main() -> None:
    """Main entry point."""
    root = Path(__file__).resolve().parents[1]
    spec_path = root / "openapi" / "openapi.json"

    if not spec_path.exists():
        print(f"❌ OpenAPI spec not found at {spec_path}")
        print("   Run: make openapi")
        return

    add_examples_to_openapi_spec(spec_path)


if __name__ == "__main__":
    main()
