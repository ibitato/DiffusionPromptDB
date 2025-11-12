import jsonlines
import json

# Load results
h45_results = list(jsonlines.open("results/realtime_results_20251112-083558.jsonl"))
s45_results = list(jsonlines.open("results/realtime_results_20251112-084001.jsonl"))

h45_stats = json.load(open("results/realtime_stats_20251112-083558.json"))
s45_stats = json.load(open("results/realtime_stats_20251112-084001.json"))

print("=" * 70)
print("COMPARISON: HAIKU 4.5 vs SONNET 4.5")
print("=" * 70)
print("\n📊 OVERALL STATISTICS\n")

print("HAIKU 4.5:")
print(f"  • Prompts analyzed: {len(h45_results)}")
print(f"  • Time per prompt: ~7.6 seconds")
print(f"  • Cost per prompt: ~$0.0043")
print(f"  • NSFW distribution: {h45_stats['nsfw_distribution']}")
print(f"  • Unique tags extracted: {len(h45_stats['common_tags'])}")
print(f"  • Top art styles: {list(h45_stats['top_art_styles'].keys())[:5]}")

print("\nSONNET 4.5:")
print(f"  • Prompts analyzed: {len(s45_results)}")
print(f"  • Time per prompt: ~13.1 seconds")
print(f"  • Cost per prompt: ~$0.0043")
print(f"  • NSFW distribution: {s45_stats['nsfw_distribution']}")
print(f"  • Unique tags extracted: {len(s45_stats['common_tags'])}")
print(f"  • Top art styles: {list(s45_stats['top_art_styles'].keys())[:5]}")

print("\n" + "=" * 70)
print("🎯 DETAILED COMPARISON - Sample Prompt #1")
print("=" * 70)

h45_sample = h45_results[0]
s45_sample = s45_results[0]

print("\n1. CHARACTER DETAILS:")
print("\nHaiku 4.5:")
print(f"  • Body types: {h45_sample['categories']['character']['body_types']}")
print(f"  • Hair styles: {h45_sample['categories']['character']['hair']['styles']}")
print(f"  • Breast size: {h45_sample['categories']['character']['breast_size']}")

print("\nSonnet 4.5:")
print(f"  • Body types: {s45_sample['categories']['character']['body_types']}")
print(f"  • Hair styles: {s45_sample['categories']['character']['hair']['styles']}")
print(f"  • Breast size: {s45_sample['categories']['character']['breast_size']}")

print("\n2. SEXUAL CONTENT:")
print("\nHaiku 4.5:")
print(f"  • Acts: {h45_sample['categories']['sexual_content']['sexual_acts'][:3]}")
print(
    f"  • Genital visibility: {h45_sample['categories']['sexual_content']['genital_visibility']}"
)

print("\nSonnet 4.5:")
print(f"  • Acts: {s45_sample['categories']['sexual_content']['sexual_acts'][:3]}")
print(
    f"  • Genital visibility: {s45_sample['categories']['sexual_content']['genital_visibility']}"
)

print("\n3. MAIN TAGS:")
print(f"\nHaiku 4.5 ({len(h45_sample['categories']['main_tags'])} tags):")
print(f"  {h45_sample['categories']['main_tags'][:10]}")

print(f"\nSonnet 4.5 ({len(s45_sample['categories']['main_tags'])} tags):")
print(f"  {s45_sample['categories']['main_tags'][:10]}")

print("\n4. TOKENS USED:")
print(f"\nHaiku 4.5: {h45_sample['metadata']['tokens_used']}")
print(f"Sonnet 4.5: {s45_sample['metadata']['tokens_used']}")

print("\n" + "=" * 70)
print("💡 QUALITY ASSESSMENT")
print("=" * 70)
