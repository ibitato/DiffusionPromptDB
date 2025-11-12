#!/usr/bin/env python3
"""Test search capabilities"""

from search_catalog import CatalogSearch

print("="*70)
print("Testing Search Capabilities")
print("="*70)

search = CatalogSearch()

# Test 1: Search by NSFW
print("\n1. Search explicit content:")
results = search.search_by_nsfw('explicit')
print(f"   Found {len(results)} results")
if results:
    print(f"   Example: ID {results[0][0]}")

# Test 2: Search by character count
print("\n2. Search prompts with 1 person:")
results = search.search_by_character_count(1)
print(f"   Found {len(results)} results")

# Test 3: Search by tag
print("\n3. Search by tag '1girl':")
results = search.search_by_tag('1girl')
print(f"   Found {len(results)} results")

# Test 4: Search by art style
print("\n4. Search anime style:")
results = search.search_by_art_style('anime')
print(f"   Found {len(results)} results")

# Test 5: Complex search
print("\n5. Complex search (explicit + 1 person + anime):")
filters = {
    'nsfw_level': 'explicit',
    'number_of_people': 1,
    'art_style': 'anime'
}
results = search.complex_search(filters)
print(f"   Found {len(results)} results")
if results:
    for i, row in enumerate(results[:3]):
        print(f"   {i+1}. ID {row[0]}: {row[1][:80]}...")

print("\n✅ All search tests completed!")
