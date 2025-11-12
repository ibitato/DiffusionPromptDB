#!/usr/bin/env python3
"""
Search Cataloged Prompts

Interactive search tool for the prompt catalog database.
"""

import sqlite3
import sys
from pathlib import Path


class CatalogSearch:
    """Search interface for prompt catalog."""

    def __init__(self, db_path: str = "prompts_catalog.db"):
        """Initialize search."""
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def search_by_nsfw(self, level: str):
        """Search prompts by NSFW level."""
        cursor = self.conn.execute(
            """
            SELECT p.id, p.original_prompt
            FROM prompts p
            JOIN nsfw_content n ON p.id = n.prompt_id
            WHERE n.level = ?
            LIMIT 10
        """,
            (level,),
        )
        return cursor.fetchall()

    def search_by_character_count(self, count: int):
        """Search prompts by number of characters."""
        cursor = self.conn.execute(
            """
            SELECT p.id, p.original_prompt, c.number_of_people
            FROM prompts p
            JOIN characters c ON p.id = c.prompt_id
            WHERE c.number_of_people = ?
            LIMIT 10
        """,
            (count,),
        )
        return cursor.fetchall()

    def search_by_hair_color(self, color: str):
        """Search prompts by hair color."""
        cursor = self.conn.execute(
            """
            SELECT DISTINCT p.id, p.original_prompt
            FROM prompts p
            JOIN character_hair h ON p.id = h.prompt_id
            WHERE h.color LIKE ?
            LIMIT 10
        """,
            (f"%{color}%",),
        )
        return cursor.fetchall()

    def search_by_tag(self, tag: str):
        """Search prompts by tag."""
        cursor = self.conn.execute(
            """
            SELECT DISTINCT p.id, p.original_prompt
            FROM prompts p
            JOIN main_tags t ON p.id = t.prompt_id
            WHERE t.tag LIKE ?
            LIMIT 10
        """,
            (f"%{tag}%",),
        )
        return cursor.fetchall()

    def search_by_art_style(self, style: str):
        """Search prompts by art style."""
        cursor = self.conn.execute(
            """
            SELECT p.id, p.original_prompt, a.primary_style
            FROM prompts p
            JOIN art_styles a ON p.id = a.prompt_id
            WHERE a.primary_style LIKE ?
            LIMIT 10
        """,
            (f"%{style}%",),
        )
        return cursor.fetchall()

    def search_by_setting(self, indoor_outdoor: str):
        """Search prompts by setting type."""
        cursor = self.conn.execute(
            """
            SELECT p.id, p.original_prompt, s.indoor_outdoor, s.specific_place
            FROM prompts p
            JOIN settings s ON p.id = s.prompt_id
            WHERE s.indoor_outdoor = ?
            LIMIT 10
        """,
            (indoor_outdoor,),
        )
        return cursor.fetchall()

    def search_by_reference(self, ref_type: str, name: str):
        """Search prompts by character/series/artist reference."""
        cursor = self.conn.execute(
            """
            SELECT DISTINCT p.id, p.original_prompt
            FROM prompts p
            JOIN prompt_references r ON p.id = r.prompt_id
            WHERE r.reference_type = ? AND r.reference_name LIKE ?
            LIMIT 10
        """,
            (ref_type, f"%{name}%"),
        )
        return cursor.fetchall()

    def complex_search(self, filters: dict):
        """
        Complex search with multiple filters.

        Example filters:
        {
            'nsfw_level': 'explicit',
            'number_of_people': 1,
            'art_style': 'anime',
            'indoor_outdoor': 'indoor'
        }
        """
        query = """
            SELECT DISTINCT p.id, p.original_prompt
            FROM prompts p
        """

        joins = []
        conditions = []
        params = []

        if "nsfw_level" in filters:
            joins.append("JOIN nsfw_content n ON p.id = n.prompt_id")
            conditions.append("n.level = ?")
            params.append(filters["nsfw_level"])

        if "number_of_people" in filters:
            joins.append("JOIN characters c ON p.id = c.prompt_id")
            conditions.append("c.number_of_people = ?")
            params.append(filters["number_of_people"])

        if "art_style" in filters:
            joins.append("JOIN art_styles a ON p.id = a.prompt_id")
            conditions.append("a.primary_style LIKE ?")
            params.append(f"%{filters['art_style']}%")

        if "indoor_outdoor" in filters:
            joins.append("JOIN settings s ON p.id = s.prompt_id")
            conditions.append("s.indoor_outdoor = ?")
            params.append(filters["indoor_outdoor"])

        if joins:
            query += " " + " ".join(joins)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " LIMIT 20"

        cursor = self.conn.execute(query, params)
        return cursor.fetchall()

    def get_available_values(self, category: str):
        """Get available values for a category."""
        queries = {
            "nsfw_levels": "SELECT DISTINCT level FROM nsfw_content",
            "art_styles": "SELECT DISTINCT primary_style FROM art_styles WHERE primary_style IS NOT NULL",
            "hair_colors": "SELECT DISTINCT color FROM character_hair WHERE color IS NOT NULL",
            "body_types": "SELECT DISTINCT body_type FROM character_body_types",
            "tags": "SELECT tag, COUNT(*) as count FROM main_tags GROUP BY tag ORDER BY count DESC LIMIT 50",
            "references": "SELECT DISTINCT reference_name FROM prompt_references ORDER BY reference_name",
        }

        if category not in queries:
            return []

        cursor = self.conn.execute(queries[category])
        return cursor.fetchall()


def interactive_search():
    """Interactive search interface."""
    print("=" * 70)
    print("Prompt Catalog Search Tool")
    print("=" * 70)
    print()

    try:
        search = CatalogSearch()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nRun import_to_db.py first to create the database.")
        return 1

    while True:
        print("\n" + "=" * 70)
        print("Search Options:")
        print("=" * 70)
        print("1. Search by NSFW level")
        print("2. Search by number of characters")
        print("3. Search by hair color")
        print("4. Search by tag")
        print("5. Search by art style")
        print("6. Search by setting (indoor/outdoor)")
        print("7. Search by character/series reference")
        print("8. Complex search (multiple filters)")
        print("9. Show available values")
        print("0. Exit")
        print()

        choice = input("Enter choice (0-9): ").strip()

        if choice == "0":
            break

        elif choice == "1":
            level = input("NSFW level (safe/suggestive/explicit): ").strip()
            results = search.search_by_nsfw(level)
            print_results(results)

        elif choice == "2":
            count = int(input("Number of people (1,2,3...): ").strip())
            results = search.search_by_character_count(count)
            print_results(results)

        elif choice == "3":
            color = input("Hair color (blonde, black, etc.): ").strip()
            results = search.search_by_hair_color(color)
            print_results(results)

        elif choice == "4":
            tag = input("Tag to search: ").strip()
            results = search.search_by_tag(tag)
            print_results(results)

        elif choice == "5":
            style = input("Art style (anime, realistic, etc.): ").strip()
            results = search.search_by_art_style(style)
            print_results(results)

        elif choice == "6":
            setting = input("Setting (indoor/outdoor): ").strip()
            results = search.search_by_setting(setting)
            print_results(results)

        elif choice == "7":
            ref_type = input("Reference type (character/series/artist): ").strip()
            name = input("Name to search: ").strip()
            results = search.search_by_reference(ref_type, name)
            print_results(results)

        elif choice == "8":
            print("\nEnter filters (leave empty to skip):")
            filters = {}

            nsfw = input("  NSFW level (safe/suggestive/explicit): ").strip()
            if nsfw:
                filters["nsfw_level"] = nsfw

            people = input("  Number of people: ").strip()
            if people:
                filters["number_of_people"] = int(people)

            style = input("  Art style: ").strip()
            if style:
                filters["art_style"] = style

            setting = input("  Setting (indoor/outdoor): ").strip()
            if setting:
                filters["indoor_outdoor"] = setting

            results = search.complex_search(filters)
            print_results(results)

        elif choice == "9":
            print("\nAvailable values:")
            print("\nNSFW Levels:")
            for row in search.get_available_values("nsfw_levels"):
                print(f"  - {row[0]}")

            print("\nTop Art Styles:")
            for row in search.get_available_values("art_styles")[:10]:
                print(f"  - {row[0]}")

            print("\nTop Tags:")
            for row in search.get_available_values("tags")[:15]:
                print(f"  - {row[0]} ({row[1]} times)")

    return 0


def print_results(results):
    """Print search results."""
    if not results:
        print("\n❌ No results found")
        return

    print(f"\n✓ Found {len(results)} results:")
    print("-" * 70)

    for row in results:
        prompt_id = row[0]
        prompt = row[1][:100] + "..." if len(row[1]) > 100 else row[1]
        print(f"\nID {prompt_id}: {prompt}")


if __name__ == "__main__":
    sys.exit(interactive_search())
