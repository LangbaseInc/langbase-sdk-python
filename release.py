#!/usr/bin/env python3
"""
Simple release script for Langbase Python SDK.
Usage: python release.py
"""

import os
import subprocess
import sys

# Fix Windows encoding issues with emojis
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    print(f"   Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        # Show both stdout and stderr
        if result.stdout.strip():
            print("📤 Output:")
            print(result.stdout)
        if result.stderr.strip():
            print("⚠️  Warnings:")
            print(result.stderr)
        if not result.stdout.strip() and not result.stderr.strip():
            print("✅ Command completed (no output)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"❌ Command that failed: {cmd}")
        if e.stdout:
            print(f"📤 Output: {e.stdout}")
        if e.stderr:
            print(f"📤 Error details: {e.stderr}")
        return False


def main():
    """Run the complete release process."""
    print("🚀 Starting Langbase SDK release process...\n")

    # Step 1: Confirm release
    try:
        confirm = input("\n❓ Proceed with release? (y/N): ").lower().strip()
        if confirm != "y" and confirm != "yes":
            print("❌ Release cancelled")
            return
    except KeyboardInterrupt:
        print("\n❌ Release cancelled")
        return

    # Step 2: Create version
    print("\n📦 Creating new version...")
    if not run_command("semantic-release version", "Creating version"):
        print("❌ Failed to create version")
        sys.exit(1)

    # Step 3: Configure git to push tags automatically (one-time setup)
    run_command(
        "git config push.followTags true", "Configuring git to push tags automatically"
    )

    # Step 4: Push everything to origin
    print("\n⬆️  Pushing to origin...")
    if not run_command("git push origin main", "Pushing commits and tags"):
        print("❌ Failed to push to origin")
        sys.exit(1)

    print("\n✅ Release completed successfully!")
    print("🎯 Next steps (optional):")
    print("   • python -m build          # Build packages")
    print("   • twine upload dist/*      # Upload to PyPI")


if __name__ == "__main__":
    main()
