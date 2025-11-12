#!/usr/bin/env python3
"""
Automated Tests for Catalog Database

Tests all search functionalities to verify the database is working correctly.
"""

import sqlite3
from pathlib import Path
import sys


class CatalogTester:
    """Test suite for catalog database."""

    def __init__(self, db_path: str = "prompts_catalog.db"):
        """Initialize with database path."""
        self.db_path = db_path
        self.conn = None
        self.passed = 0
        self.failed = 0

    def __enter__(self):
        """Connect to database."""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection."""
        if self.conn:
            self.conn.close()

    def test(self, name: str, condition: bool, details: str = ""):
        """Record test result."""
        if condition:
            print(f"  ✅ {name}")
            if details:
                print(f"     {details}")
            self.passed += 1
        else:
            print(f"  ❌ {name}")
            if details:
                print(f"     {details}")
            self.failed += 1
        return condition

    def test_basic_stats(self):
        """Test 1: Basic database statistics."""
        print("\n🔹 Test 1: Basic Statistics")

        cursor = self.conn.cursor()

        # Total prompts
        total = cursor.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
        self.test("Database has prompts", total > 10000, f"Found {total:,} prompts")

        # NSFW distribution
        nsfw_dist = cursor.execute(
            """
            SELECT level, COUNT(*) as count 
            FROM nsfw_content 
            GROUP BY level
        """
        ).fetchall()

        self.test(
            "NSFW levels populated",
            len(nsfw_dist) >= 3,
            f"Found {len(nsfw_dist)} NSFW levels",
        )

        # Character data
        char_count = cursor.execute("SELECT COUNT(*) FROM characters").fetchone()[0]
        self.test(
            "Character data exists",
            char_count > 10000,
            f"{char_count:,} character records",
        )

        # Main tags
        tag_count = cursor.execute(
            "SELECT COUNT(DISTINCT tag) FROM main_tags"
        ).fetchone()[0]
        self.test("Tags extracted", tag_count > 1000, f"{tag_count:,} unique tags")

    def test_nsfw_search(self):
        """Test 2: NSFW level search."""
        print("\n🔹 Test 2: NSFW Level Search")

        cursor = self.conn.cursor()

        # Search explicit
        explicit = cursor.execute(
            """
            SELECT COUNT(*) FROM nsfw_content WHERE level = 'explicit'
        """
        ).fetchone()[0]
        self.test(
            "Search explicit content",
            explicit > 5000,
            f"Found {explicit:,} explicit prompts",
        )

        # Search safe
        safe = cursor.execute(
            """
            SELECT COUNT(*) FROM nsfw_content WHERE level = 'safe'
        """
        ).fetchone()[0]
        self.test("Search safe content", safe > 0, f"Found {safe:,} safe prompts")

        # Search suggestive
        suggestive = cursor.execute(
            """
            SELECT COUNT(*) FROM nsfw_content WHERE level = 'suggestive'
        """
        ).fetchone()[0]
        self.test(
            "Search suggestive content",
            suggestive > 0,
            f"Found {suggestive:,} suggestive prompts",
        )

    def test_character_search(self):
        """Test 3: Character-based search."""
        print("\n🔹 Test 3: Character Search")

        cursor = self.conn.cursor()

        # Single character
        solo = cursor.execute(
            """
            SELECT COUNT(*) FROM characters WHERE number_of_people = 1
        """
        ).fetchone()[0]
        self.test("Search solo characters", solo > 5000, f"Found {solo:,} solo prompts")

        # Couples
        couples = cursor.execute(
            """
            SELECT COUNT(*) FROM characters WHERE number_of_people = 2
        """
        ).fetchone()[0]
        self.test("Search couples", couples > 3000, f"Found {couples:,} couple prompts")

        # Groups
        groups = cursor.execute(
            """
            SELECT COUNT(*) FROM characters WHERE number_of_people >= 3
        """
        ).fetchone()[0]
        self.test("Search groups", groups > 400, f"Found {groups:,} group prompts")

    def test_art_style_search(self):
        """Test 4: Art style search."""
        print("\n🔹 Test 4: Art Style Search")

        cursor = self.conn.cursor()

        # Anime style
        anime = cursor.execute(
            """
            SELECT COUNT(*) FROM art_styles WHERE primary_style = 'anime'
        """
        ).fetchone()[0]
        self.test("Search anime style", anime > 1000, f"Found {anime:,} anime prompts")

        # Realistic
        realistic = cursor.execute(
            """
            SELECT COUNT(*) FROM art_styles WHERE primary_style = 'realistic'
        """
        ).fetchone()[0]
        self.test(
            "Search realistic style",
            realistic > 2000,
            f"Found {realistic:,} realistic prompts",
        )

        # Photorealistic
        photo = cursor.execute(
            """
            SELECT COUNT(*) FROM art_styles WHERE primary_style = 'photorealistic'
        """
        ).fetchone()[0]
        self.test(
            "Search photorealistic style",
            photo > 0,
            f"Found {photo:,} photorealistic prompts",
        )

    def test_tag_search(self):
        """Test 5: Tag-based search."""
        print("\n🔹 Test 5: Tag Search")

        cursor = self.conn.cursor()

        # Most popular tag (1girl)
        girl_tag = cursor.execute(
            """
            SELECT COUNT(*) FROM main_tags WHERE tag = '1girl'
        """
        ).fetchone()[0]
        self.test(
            "Search '1girl' tag",
            girl_tag > 5000,
            f"Found {girl_tag:,} prompts with '1girl'",
        )

        # Masterpiece tag
        masterpiece = cursor.execute(
            """
            SELECT COUNT(*) FROM main_tags WHERE tag = 'masterpiece'
        """
        ).fetchone()[0]
        self.test(
            "Search 'masterpiece' tag",
            masterpiece > 3000,
            f"Found {masterpiece:,} prompts with 'masterpiece'",
        )

        # Nude tag
        nude = cursor.execute(
            """
            SELECT COUNT(*) FROM main_tags WHERE tag = 'nude'
        """
        ).fetchone()[0]
        self.test(
            "Search 'nude' tag", nude > 2000, f"Found {nude:,} prompts with 'nude'"
        )

    def test_complex_search(self):
        """Test 6: Complex multi-filter search."""
        print("\n🔹 Test 6: Complex Multi-Filter Search")

        cursor = self.conn.cursor()

        # Explicit + 1 girl + anime
        result1 = cursor.execute(
            """
            SELECT COUNT(*)
            FROM prompts p
            JOIN nsfw_content n ON p.id = n.prompt_id
            JOIN characters c ON p.id = c.prompt_id
            JOIN art_styles a ON p.id = a.prompt_id
            WHERE n.level = 'explicit'
            AND c.number_of_people = 1
            AND a.primary_style = 'anime'
        """
        ).fetchone()[0]
        self.test(
            "Complex: explicit + 1 girl + anime",
            result1 > 100,
            f"Found {result1:,} matching prompts",
        )

        # Realistic + couple
        result2 = cursor.execute(
            """
            SELECT COUNT(*)
            FROM prompts p
            JOIN characters c ON p.id = c.prompt_id
            JOIN art_styles a ON p.id = a.prompt_id
            WHERE c.number_of_people = 2
            AND a.primary_style = 'realistic'
        """
        ).fetchone()[0]
        self.test(
            "Complex: realistic + couple",
            result2 > 100,
            f"Found {result2:,} matching prompts",
        )

        # Suggestive + long hair
        result3 = cursor.execute(
            """
            SELECT COUNT(DISTINCT p.id)
            FROM prompts p
            JOIN nsfw_content n ON p.id = n.prompt_id
            JOIN main_tags t ON p.id = t.prompt_id
            WHERE n.level = 'suggestive'
            AND t.tag = 'long hair'
        """
        ).fetchone()[0]
        self.test(
            "Complex: suggestive + long hair",
            result3 > 10,
            f"Found {result3:,} matching prompts",
        )

    def test_data_integrity(self):
        """Test 7: Data integrity checks."""
        print("\n🔹 Test 7: Data Integrity")

        cursor = self.conn.cursor()

        # All prompts have NSFW classification
        prompts_total = cursor.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
        nsfw_total = cursor.execute("SELECT COUNT(*) FROM nsfw_content").fetchone()[0]
        self.test(
            "All prompts classified for NSFW",
            prompts_total == nsfw_total,
            f"{nsfw_total:,}/{prompts_total:,} classified",
        )

        # All prompts have character data
        char_total = cursor.execute("SELECT COUNT(*) FROM characters").fetchone()[0]
        self.test(
            "All prompts have character data",
            char_total == prompts_total,
            f"{char_total:,}/{prompts_total:,} have character data",
        )

        # Main tags populated
        tags_total = cursor.execute("SELECT COUNT(*) FROM main_tags").fetchone()[0]
        self.test(
            "Main tags extracted",
            tags_total > 100000,
            f"{tags_total:,} total tag entries",
        )

        # No orphaned records
        orphaned = cursor.execute(
            """
            SELECT COUNT(*) FROM nsfw_content 
            WHERE prompt_id NOT IN (SELECT id FROM prompts)
        """
        ).fetchone()[0]
        self.test(
            "No orphaned NSFW records", orphaned == 0, f"{orphaned} orphaned records"
        )

    def test_indexes(self):
        """Test 8: Index performance."""
        print("\n🔹 Test 8: Index Performance")

        cursor = self.conn.cursor()

        # Check indexes exist
        indexes = cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='index' AND sql IS NOT NULL
        """
        ).fetchall()

        index_names = [idx[0] for idx in indexes]

        self.test("NSFW level index exists", "idx_nsfw_level" in index_names)
        self.test("Art style index exists", "idx_art_style" in index_names)
        self.test(
            "Character gender index exists", "idx_character_gender" in index_names
        )
        self.test("Main tags index exists", "idx_main_tags" in index_names)
        self.test(
            "People count index exists", "idx_characters_people_count" in index_names
        )

    def test_sample_queries(self):
        """Test 9: Sample realistic queries."""
        print("\n🔹 Test 9: Sample API-Style Queries")

        cursor = self.conn.cursor()

        # Query 1: Explicit anime 1girl
        result = cursor.execute(
            """
            SELECT p.id, p.original_prompt, n.level, a.primary_style
            FROM prompts p
            JOIN nsfw_content n ON p.id = n.prompt_id
            JOIN characters c ON p.id = c.prompt_id
            JOIN art_styles a ON p.id = a.prompt_id
            WHERE n.level = 'explicit'
            AND c.number_of_people = 1
            AND a.primary_style = 'anime'
            LIMIT 5
        """
        ).fetchall()

        self.test(
            "Query returns results",
            len(result) > 0,
            f"Got {len(result)} sample results",
        )

        # Query 2: Top tags analysis
        top_tags = cursor.execute(
            """
            SELECT tag, COUNT(*) as count
            FROM main_tags
            GROUP BY tag
            ORDER BY count DESC
            LIMIT 5
        """
        ).fetchall()

        self.test("Tag aggregation works", len(top_tags) == 5)
        if top_tags:
            top_tag = top_tags[0]
            print(f"     Top tag: '{top_tag[0]}' appears {top_tag[1]:,} times")

        # Query 3: NSFW distribution
        nsfw_dist = cursor.execute(
            """
            SELECT level, COUNT(*) as count
            FROM nsfw_content
            GROUP BY level
        """
        ).fetchall()

        self.test("NSFW distribution query works", len(nsfw_dist) >= 3)
        for level_row in nsfw_dist:
            print(f"     {level_row[0]}: {level_row[1]:,} prompts")

    def run_all_tests(self):
        """Run all test suites."""
        print("=" * 70)
        print("CATALOG DATABASE TEST SUITE")
        print("=" * 70)
        print(f"\nDatabase: {self.db_path}")
        print(f"Location: {Path(self.db_path).absolute()}")

        # Run tests
        self.test_basic_stats()
        self.test_nsfw_search()
        self.test_character_search()
        self.test_art_style_search()
        self.test_tag_search()
        self.test_complex_search()
        self.test_data_integrity()
        self.test_indexes()
        self.test_sample_queries()

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0

        print(f"\n✅ Passed: {self.passed}/{total_tests}")
        print(f"❌ Failed: {self.failed}/{total_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! Database is ready for production.")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Review errors above.")

        return self.failed == 0


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test catalog database")
    parser.add_argument("--db", default="prompts_catalog.db", help="Database file path")

    args = parser.parse_args()

    try:
        with CatalogTester(args.db) as tester:
            success = tester.run_all_tests()
            return 0 if success else 1
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
