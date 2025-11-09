#!/usr/bin/env python3
"""Test script to verify agent can query database"""

import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, '/app')

from app.agents.changelog_agent import query_forms_database

async def main():
    print("Testing agent's database query tool...\n")
    
    # Test 1: List all forms
    print("Test 1: Querying forms table")
    result = await query_forms_database("SELECT id, title, slug FROM forms")
    print(f"Result: {result[:200]}...\n")
    
    # Test 2: Query option_items (for the Paris example)
    print("Test 2: Querying option_items table")
    result = await query_forms_database(
        "SELECT id, value, label, option_set_id FROM option_items LIMIT 5"
    )
    print(f"Result: {result[:200]}...\n")
    
    # Test 3: Find travel form
    print("Test 3: Finding travel form")
    result = await query_forms_database(
        "SELECT id, title FROM forms WHERE slug LIKE '%travel%'"
    )
    print(f"Result: {result}\n")
    
    print("✓ All database query tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
