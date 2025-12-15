#!/usr/bin/env python3
"""
Test script to query sample result from Affine API.
Mimics the behavior of 'af get-sample' command.
"""

import asyncio
import json
import sys
import os
from typing import Optional

# Add the affine package to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    from affine.utils.api_client import cli_api_client
except ImportError:
    print("Error: Could not import affine.utils.api_client")
    print("Make sure you're running this from the affine-cortex directory")
    sys.exit(1)


async def get_sample(uid: int, env: str, task_id: str, base_url: Optional[str] = None):
    """
    Query sample result by UID, environment, and task ID.
    
    Args:
        uid: Miner UID
        env: Environment name (e.g., "agentgym:webshop", "affine:ded")
        task_id: Task ID
        base_url: Optional custom API base URL (defaults to API_URL env var or https://api.affine.io/api/v1)
    """
    print(f"Querying sample: UID={uid}, Environment={env}, Task ID={task_id}")
    print("-" * 60)
    
    # Use custom base_url if provided, otherwise let cli_api_client use default
    if base_url:
        async with cli_api_client(base_url=base_url) as client:
            endpoint = f"/samples/uid/{uid}/{env}/{task_id}"
            print(f"API Endpoint: {client.base_url}{endpoint}")
            data = await client.get(endpoint)
    else:
        async with cli_api_client() as client:
            endpoint = f"/samples/uid/{uid}/{env}/{task_id}"
            print(f"API Endpoint: {client.base_url}{endpoint}")
            data = await client.get(endpoint)
    
    if data:
        print("\n✅ Sample retrieved successfully:")
        print("=" * 60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data
    else:
        print("\n❌ No data returned from API")
        return None


def main():
    """Main function to handle command-line input."""
    print("=" * 60)
    print("Affine Sample Query Test")
    print("=" * 60)
    print()
    
    # Get input from command line arguments or prompt
    if len(sys.argv) >= 4:
        uid = int(sys.argv[1])
        env = sys.argv[2]
        task_id = sys.argv[3]
        base_url = sys.argv[4] if len(sys.argv) > 4 else None
    else:
        # Interactive mode
        print("Enter sample query parameters:")
        try:
            uid = int(input("UID: "))
            env = input("Environment (e.g., agentgym:webshop, affine:ded): ")
            task_id = input("Task ID: ")
            # base_url_input = input("Base URL (optional, press Enter for default): ").strip()
            # base_url = base_url_input if base_url_input else None
            base_url = None
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid input or cancelled")
            sys.exit(1)
    
    print()
    
    # Run async function
    try:
        result = asyncio.run(get_sample(uid, env, task_id, base_url))
        
        if result:
            print("\n" + "=" * 60)
            print("✅ Test completed successfully")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ Test failed - no data returned")
            print("=" * 60)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

