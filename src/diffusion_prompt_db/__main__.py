"""
CLI entry point for DiffusionPromptDB.
"""

import sys
from .database import Database
from .models import Prompt


def main():
    """Main CLI function."""
    print("DiffusionPromptDB v0.1.0")
    print("=" * 50)

    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    try:
        if command == "init":
            init_database()
        elif command == "add":
            add_prompt_interactive()
        elif command == "list":
            list_prompts()
        elif command == "search":
            search_prompts_interactive()
        else:
            print(f"Unknown command: {command}")
            print_usage()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def print_usage():
    """Print usage information."""
    print("\nUsage: diffusion-prompt-db <command>")
    print("\nCommands:")
    print("  init     - Initialize the database")
    print("  add      - Add a new prompt (interactive)")
    print("  list     - List all prompts")
    print("  search   - Search prompts (interactive)")
    print("\nExample:")
    print("  diffusion-prompt-db init")
    print("  diffusion-prompt-db list")


def init_database():
    """Initialize the database."""
    print("Initializing database...")
    with Database() as db:
        print(f"✓ Database initialized at: {db.db_path}")
        print("✓ Tables created successfully")


def add_prompt_interactive():
    """Add a prompt interactively."""
    print("\nAdd New Prompt")
    print("-" * 50)

    text = input("Prompt text: ").strip()
    if not text:
        print("Error: Prompt text cannot be empty")
        return

    negative_prompt = input("Negative prompt (optional): ").strip() or None
    model = input("Model (optional): ").strip() or None
    category = input("Category (optional): ").strip() or None
    tags = input("Tags (comma-separated, optional): ").strip() or None

    rating_input = input("Rating 1-5 (optional): ").strip()
    rating = int(rating_input) if rating_input else None

    notes = input("Notes (optional): ").strip() or None

    prompt = Prompt(
        text=text,
        negative_prompt=negative_prompt,
        model=model,
        category=category,
        tags=tags,
        rating=rating,
        notes=notes,
    )

    with Database() as db:
        prompt_id = db.add_prompt(prompt)
        print(f"\n✓ Prompt added successfully with ID: {prompt_id}")


def list_prompts():
    """List all prompts."""
    with Database() as db:
        prompts = db.get_all_prompts(limit=20)

        if not prompts:
            print("No prompts found in database.")
            return

        print(f"\nFound {len(prompts)} prompt(s):\n")

        for prompt in prompts:
            print(f"ID: {prompt.id}")
            print(f"Text: {prompt.text[:80]}{'...' if len(prompt.text) > 80 else ''}")
            if prompt.model:
                print(f"Model: {prompt.model}")
            if prompt.category:
                print(f"Category: {prompt.category}")
            if prompt.rating:
                print(f"Rating: {'⭐' * prompt.rating}")
            print(f"Created: {prompt.created_at}")
            print("-" * 50)


def search_prompts_interactive():
    """Search prompts interactively."""
    print("\nSearch Prompts")
    print("-" * 50)

    text = input("Search text (optional): ").strip() or None
    category = input("Category (optional): ").strip() or None
    model = input("Model (optional): ").strip() or None

    min_rating_input = input("Minimum rating (optional): ").strip()
    min_rating = int(min_rating_input) if min_rating_input else None

    with Database() as db:
        prompts = db.search_prompts(
            text=text, category=category, model=model, min_rating=min_rating
        )

        if not prompts:
            print("\nNo prompts found matching criteria.")
            return

        print(f"\nFound {len(prompts)} prompt(s):\n")

        for prompt in prompts:
            print(f"ID: {prompt.id}")
            print(f"Text: {prompt.text[:80]}{'...' if len(prompt.text) > 80 else ''}")
            if prompt.model:
                print(f"Model: {prompt.model}")
            if prompt.category:
                print(f"Category: {prompt.category}")
            if prompt.rating:
                print(f"Rating: {'⭐' * prompt.rating}")
            print("-" * 50)


if __name__ == "__main__":
    main()
