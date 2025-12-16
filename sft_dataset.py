#!/usr/bin/env python3
"""
SFT Data Generator - Query samples from Affine API and generate training data.
Uses standard functions from affine.src.miner.commands.
"""

import asyncio
import json
import sys
import os
from typing import Optional, List, Dict, Any

# Add the affine package to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    from affine.utils.api_client import cli_api_client
    from affine.src.miner.commands import get_sample_command, get_pool_command
except ImportError as e:
    print(f"Error: Could not import affine modules: {e}")
    print("Make sure you're running this from the affine-cortex directory")
    sys.exit(1)


async def get_sample_data(uid: int, env: str, task_id: str, base_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Query sample result by UID, environment, and task ID.
    Returns data instead of printing (wrapper around standard get_sample_command).
    
    Args:
        uid: Miner UID
        env: Environment name (e.g., "agentgym:webshop", "affine:ded")
        task_id: Task ID
        base_url: Optional custom API base URL (defaults to API_URL env var or https://api.affine.io/api/v1)
    
    Returns:
        Sample data dictionary or None if not found
    """
    # Use the same logic as get_sample_command but return data instead of printing
    if base_url:
        async with cli_api_client(base_url=base_url) as client:
            endpoint = f"/samples/uid/{uid}/{env}/{task_id}"
            data = await client.get(endpoint)
    else:
        async with cli_api_client() as client:
            endpoint = f"/samples/uid/{uid}/{env}/{task_id}"
            data = await client.get(endpoint)
    
    return data


async def get_pool_data(uid: int, env: str, full: bool = True, base_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Query task pool status for a miner in an environment.
    Returns data instead of printing (wrapper around standard get_pool_command).
    
    Args:
        uid: Miner UID
        env: Environment name (e.g., "agentgym:webshop")
        full: If True, return full task_ids lists without truncation
        base_url: Optional custom API base URL
    
    Returns:
        Pool data dictionary or None if not found
    """
    # Use the same logic as get_pool_command but return data instead of printing
    try:
        if base_url:
            async with cli_api_client(base_url=base_url) as client:
                endpoint = f"/samples/pool/uid/{uid}/{env}"
                data = await client.get(endpoint)
        else:
            async with cli_api_client() as client:
                endpoint = f"/samples/pool/uid/{uid}/{env}"
                data = await client.get(endpoint)
        
        if data is None:
            print(f"  ⚠️  UID {uid}: API returned None")
            return None
        
        if data.get("success") is False:
            print(f"  ⚠️  UID {uid}: API returned success=False, response: {data}")
            return None
        
        return data
    except Exception as e:
        print(f"  ❌ UID {uid}: Exception in get_pool_data: {e}")
        return None


def write_jsonl(path: str, rows: List[Dict[str, Any]]):
    """
    Write a list of dictionaries to a JSONL file.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def writedata(path: str, data: str):
    """
    Write a string to a data file.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(data + "\n")

def read_jsonl(path: str) -> List[Dict[str, Any]]:
    """
    Read JSONL file and return list of dictionaries.
    Handles both single-line and multi-line JSON objects.
    """
    if not os.path.exists(path):
        return []
    
    data_list = []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse JSONL by finding complete JSON objects
    # Accumulate characters until braces are balanced
    current_obj = ""
    brace_count = 0
    in_string = False
    escape_next = False
    
    for char in content:
        current_obj += char
        
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                
                # When braces are balanced, we have a complete JSON object
                if brace_count == 0 and current_obj.strip():
                    try:
                        obj = json.loads(current_obj.strip())
                        if isinstance(obj, dict):
                            data_list.append(obj)
                    except json.JSONDecodeError:
                        pass  # Skip malformed JSON
                    current_obj = ""
    
    return data_list

def preprocess(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocess the sample data.
    """
    extra = data.get('extra', {})
    conversation = extra.get('conversation', [])
    env = data.get('env', '')
    task_id = data.get('task_id', 0)
    reward = data.get('score', 0.0)
    seed = extra.get('seed', 0)
    success = reward > 0.95
    return {
        "conversation": conversation,
        "env": env,
        "task_id": task_id,
        "reward": reward,
        "success": success,
        "seed": seed
    }

def main():
    """Main function to handle command-line input."""
    print("=" * 60)
    print("Affine Sample Query Test")
    print("=" * 60)
    print()

    task_ids = {
        "affine:abd-v2":[0] * 30000,
        "affine:ded-v2":[0] * 30000,
        "agentgym:alfworld":[0] * 30000,
        "agentgym:sciworld":[0] * 30000,
        "agentgym:textcraft":[0] * 30000,
        "agentgym:webshop":[0] * 30000,
        "LGC":[0] * 30000,
        "MTH":[0] * 30000,
        "SCI":[0] * 30000,
        "CDE":[0] * 30000,
    }
    # Example: Get pool data for a specific UID and environment
    # uid_list = [3, 174, 50, 157, 245, 0, 243, 142, 118, 86, 30, 209, 16, 177]
    uid_list = [101, 23, 54, 18]
    env = "agentgym:sciworld"
    if sys.argv[1]:
        env = sys.argv[1]
    base_url = None

    # Load existing data to track which task_ids we already have
    existing_data = read_jsonl("sft_data.jsonl")
    data_list = []
    
    env_name = env

    existing_data = read_jsonl("sft_data.jsonl")

    _cnt = 0
    for data in existing_data:
        if isinstance(data, dict) and data.get('task_id') is not None:
            if data['env'].lower() == env_name.lower():
                data['env'] = env_name
            if data['env'] != env_name:
                continue
            if task_ids[env_name][data['task_id']] == 1:
                continue
            task_ids[env_name][data['task_id']] = 1
            # print(f"✅ {env_name} {data['task_id']}")
            _cnt += 1
            data_list.append(data)  # Keep existing data

    print(f"✅ {env_name} ({env_name}): {_cnt} tasks already retrieved")
    con_cnt = 0

    for uid in uid_list:
        print(f"Processing UID {uid}...")
        try:
            pool_result = asyncio.run(get_pool_data(uid, env, full=True, base_url=None))
        except Exception as e:
            print(f"  ❌ Error retrieving pool for UID {uid}: {e}")
            continue
        if pool_result:
            sampled_task_ids = pool_result.get('sampled_task_ids', [])
            # print(f"✅ {len(sampled_task_ids)} & {sampled_task_ids[:10]} tasks sampled")
            for task_id in sampled_task_ids:
                if task_id < 20527:
                    continue
                # print(task_id)
                if task_ids[env_name][task_id] == 0:
                    # task_id is currently empty, so we can add it to the list
                    try:
                        result = asyncio.run(get_sample_data(uid, env, task_id, base_url))
                    except Exception as e:
                        print(f"Error retrieving sample: {e}")
                        con_cnt += 1
                        continue
                    if result:
                        data = preprocess(result)
                        if data['reward'] > 0.95:
                            task_ids[env_name][task_id] = 1
                            write_jsonl("sft_data.jsonl", [data])
                            # data_list.append(data)
                            print(f"✅ Sample {task_id} retrieved")
                            con_cnt = 0
                        else:
                            print(f"❌ Sample {task_id} failed with reward {data['reward']}")
                            con_cnt += 1
                            if con_cnt >= 30:
                                break

    cnt = 0
    for task_id in task_ids[env_name]:
        if task_id == 1:
            cnt += 1
    print(f"✅ {cnt} tasks retrieved")
    if cnt > 0:
        # write_jsonl("sft_data.jsonl", data_list)
        print(f"✅ Saved {len(data_list)} & {cnt} tasks to sft_data.jsonl")
    else:
        print("❌ No tasks retrieved")


if __name__ == "__main__":
    main()

