#!/usr/bin/env python3
"""
Simple standalone test script to query sample result from Affine API.
Does not require the affine package - uses direct HTTP requests.
"""

import asyncio
import json
import sys
import os
from typing import Optional

try:
    import aiohttp
except ImportError:
    print("Error: aiohttp is required. Install with: pip install aiohttp")
    sys.exit(1)


async def get_sample_simple(uid: int, env: str, task_id: str, base_url: Optional[str] = None):
    """
    Query sample result by UID, environment, and task ID.
    
    Args:
        uid: Miner UID
        env: Environment name (e.g., "agentgym:webshop", "affine:ded")
        task_id: Task ID
        base_url: Optional custom API base URL (defaults to API_URL env var or https://api.affine.io/api/v1)
    """
    # Get base URL from environment or use default
    if base_url is None:
        base_url = os.getenv("API_URL", "https://api.affine.io/api/v1")
    
    endpoint = f"/samples/uid/{uid}/{env}/{task_id}"
    url = f"{base_url.rstrip('/')}{endpoint}"
    
    print(f"Querying sample: UID={uid}, Environment={env}, Task ID={task_id}")
    print("-" * 60)
    print(f"API URL: {url}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Sample retrieved successfully:")
                    print("=" * 60)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    return data
                else:
                    error_text = await response.text()
                    print(f"❌ API Error (Status {response.status}):")
                    print(error_text)
                    return None
    except aiohttp.ClientError as e:
        print(f"❌ Network Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        return None


def main():
    """Main function to handle command-line input."""
    print("=" * 60)
    print("Affine Sample Query Test (Simple Version)")
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
            base_url_input = input("Base URL (optional, press Enter for default): ").strip()
            base_url = base_url_input if base_url_input else None
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid input or cancelled")
            sys.exit(1)
    
    print()
    
    # Run async function
    try:
        result = asyncio.run(get_sample_simple(uid, env, task_id, base_url))
        
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

