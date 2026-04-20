"""Manual API test for audit rights workflow endpoints.

This script tests the audit rights API endpoints to verify:
1. Workflow creation
2. Workflow listing
3. Demand letter generation
4. Status updates
"""

import json
import requests
from datetime import datetime, timezone, timedelta

# Base URL (adjust if needed)
BASE_URL = "http://localhost:8000"

def test_audit_workflow_api():
    """Test audit rights workflow API endpoints."""
    
    print("=" * 60)
    print("AUDIT RIGHTS WORKFLOW API TEST")
    print("=" * 60)
    
    # Test artist ID (replace with actual artist ID from your database)
    artist_id = "test-artist-001"
    
    # 1. Create a new audit workflow
    print("\n1. Creating audit workflow...")
    create_payload = {
        "artist_id": artist_id,
        "contract_id": "contract-abc-123",
        "counterparty_name": "Test Record Label Inc.",
        "counterparty_address": "123 Music Row, Nashville, TN 37203",
        "counterparty_contact": "Legal Department - contracts@testlabel.com",
        "audit_period_start": "2023-01-01T00:00:00Z",
        "audit_period_end": "2025-12-31T23:59:59Z",
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/artists/{artist_id}/audit-workflows",
            json=create_payload,
            headers={"Content-Type": "application/json"},
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            workflow = response.json()
            workflow_id = workflow["id"]
            print(f"   ✓ Workflow created: {workflow_id}")
            print(f"   Status: {workflow['status']}")
        else:
            print(f"   ✗ Failed: {response.text}")
            return
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # 2. List workflows for artist
    print("\n2. Listing workflows...")
    try:
        response = requests.get(f"{BASE_URL}/artists/{artist_id}/audit-workflows")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            workflows = response.json()
            print(f"   ✓ Found {len(workflows)} workflow(s)")
        else:
            print(f"   ✗ Failed: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 3. Generate demand letter
    print("\n3. Generating audit demand letter...")
    proposed_date = (datetime.now(timezone.utc) + timedelta(days=45)).isoformat()
    
    letter_payload = {
        "artist_name": "Test Artist Legal Name",
        "contract_name": "Exclusive Recording Agreement",
        "contract_date": "January 15, 2020",
        "audit_clause_reference": "Section 12.3",
        "proposed_audit_date": proposed_date,
        "attorney_name": "Jane Doe, Esq.",
        "auditor_name": "Smith & Associates CPA",
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/artists/{artist_id}/audit-workflows/{workflow_id}/generate-letter",
            json=letter_payload,
            headers={"Content-Type": "application/json"},
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            letter_text = response.text
            print(f"   ✓ Letter generated ({len(letter_text)} characters)")
            print("\n   Letter preview (first 500 chars):")
            print("   " + "-" * 56)
            print("   " + letter_text[:500].replace("\n", "\n   "))
            print("   " + "-" * 56)
        else:
            print(f"   ✗ Failed: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 4. Update workflow status to LETTER_SENT
    print("\n4. Updating workflow status to LETTER_SENT...")
    try:
        response = requests.patch(
            f"{BASE_URL}/artists/{artist_id}/audit-workflows/{workflow_id}",
            json={"status": "LETTER_SENT"},
            headers={"Content-Type": "application/json"},
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            updated = response.json()
            print(f"   ✓ Status updated: {updated['status']}")
            print(f"   Letter sent at: {updated.get('letter_sent_at', 'N/A')}")
        else:
            print(f"   ✗ Failed: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 5. Get workflow stats
    print("\n5. Getting system-wide stats...")
    try:
        response = requests.get(f"{BASE_URL}/audit-workflows/stats")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✓ Total workflows: {stats['total_workflows']}")
            print(f"   By status: {json.dumps(stats['by_status'], indent=6)}")
        else:
            print(f"   ✗ Failed: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    print("\nNOTE: This test requires:")
    print("  1. API server running: python -m uvicorn XR7.api.app:app --reload")
    print("  2. Test artist in database with ID 'test-artist-001'")
    print("  3. or modify artist_id variable above")
    print()
    
    input("Press Enter to continue with API test...")
    test_audit_workflow_api()
