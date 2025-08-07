#!/usr/bin/env python3
"""
Interactive release script for Langbase Python SDK.
Usage: python release.py
"""

import os
import re
import subprocess
import sys
from datetime import datetime

# Fix Windows encoding issues with emojis
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"


def run_command(cmd, description, capture_output=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    print(f"   Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=capture_output,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if capture_output:
            # Show both stdout and stderr
            if result.stdout.strip():
                print("📤 Output:")
                print(result.stdout)
            if result.stderr.strip():
                print("⚠️  Warnings:")
                print(result.stderr)
            if not result.stdout.strip() and not result.stderr.strip():
                print("✅ Command completed (no output)")
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"❌ Command that failed: {cmd}")
        if e.stdout:
            print(f"📤 Output: {e.stdout}")
        if e.stderr:
            print(f"📤 Error details: {e.stderr}")
        return False, ""


def get_current_version():
    """Get current version from pyproject.toml."""
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'version = "([^"]+)"', content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    return "0.0.0"


def parse_version(version):
    """Parse version string into major, minor, patch."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_version(current_version, bump_type):
    """Bump version based on type."""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_version_files(new_version):
    """Update version in pyproject.toml and __init__.py."""
    print(f"📝 Updating version to {new_version}...")

    # Update pyproject.toml
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)

        with open("pyproject.toml", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Updated pyproject.toml")
    except Exception as e:
        print(f"❌ Failed to update pyproject.toml: {e}")
        return False

    # Update __init__.py
    try:
        with open("langbase/__init__.py", "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(
            r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content
        )

        with open("langbase/__init__.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Updated langbase/__init__.py")
    except Exception as e:
        print(f"❌ Failed to update langbase/__init__.py: {e}")
        return False

    return True


def update_changelog(version, release_message):
    """Update CHANGELOG.md with new release."""
    print("📝 Updating CHANGELOG.md...")

    try:
        # Read current changelog
        try:
            with open("CHANGELOG.md", "r", encoding="utf-8") as f:
                current_content = f.read()
        except FileNotFoundError:
            current_content = "# Changelog\n\n"

        # Create new entry
        date = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"## [{version}] - {date}\n\n{release_message}\n\n"

        # Insert after the header
        if "# Changelog" in current_content:
            parts = current_content.split("# Changelog\n", 1)
            updated_content = f"# Changelog\n\n{new_entry}" + (
                parts[1] if len(parts) > 1 else ""
            )
        else:
            updated_content = f"# Changelog\n\n{new_entry}{current_content}"

        with open("CHANGELOG.md", "w", encoding="utf-8") as f:
            f.write(updated_content)

        print("✅ Updated CHANGELOG.md")
        return True
    except Exception as e:
        print(f"❌ Failed to update CHANGELOG.md: {e}")
        return False


def ask_yes_no(question):
    """Ask a yes/no question."""
    while True:
        try:
            answer = input(f"\n❓ {question} (y/n): ").lower().strip()
            if answer in ["y", "yes"]:
                return True
            elif answer in ["n", "no", ""]:
                return False
            else:
                print("Please answer 'y' or 'n'")
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            sys.exit(1)


def main():
    """Run the interactive release process."""
    print("🚀 Starting Interactive Langbase SDK Release Process...\n")

    # Ask if this is a test release
    test_mode = ask_yes_no(
        "Is this a TEST release? (uploads to test.pypi.org instead of PyPI)"
    )
    if test_mode:
        print("🧪 TEST MODE: Will upload to test.pypi.org")

    # Get current version
    current_version = get_current_version()
    print(f"📋 Current version: {current_version}")

    # Step 1: Ask for version bump type
    print("\n📈 What type of release is this?")
    print("   • patch  - Bug fixes, small improvements (0.1.0 → 0.1.1)")
    print("   • minor  - New features, backwards compatible (0.1.0 → 0.2.0)")
    print("   • major  - Breaking changes (0.1.0 → 1.0.0)")

    while True:
        try:
            bump_type = (
                input("\n❓ Enter release type (patch/minor/major): ").lower().strip()
            )
            if bump_type in ["patch", "minor", "major"]:
                break
            else:
                print("Please enter 'patch', 'minor', or 'major'")
        except KeyboardInterrupt:
            print("\n❌ Release cancelled")
            sys.exit(1)

    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"\n📋 New version will be: {current_version} → {new_version}")

    # Step 2: Confirm version update
    if not ask_yes_no(f"Update version to {new_version}?"):
        print("❌ Release cancelled")
        return

    # Step 3: Get release message
    print(f"\n📝 Enter release message for v{new_version}:")
    print("   (Describe what's new, changed, or fixed)")
    try:
        release_message = input("Release message: ").strip()
        if not release_message:
            release_message = f"Release v{new_version}"
    except KeyboardInterrupt:
        print("\n❌ Release cancelled")
        sys.exit(1)

    # Step 4: Show preview and confirm
    print(f"\n📋 Release Summary:")
    print(f"   Version: {current_version} → {new_version}")
    print(f"   Type: {bump_type}")
    print(f"   Message: {release_message}")
    if test_mode:
        print("   🧪 Destination: Test PyPI (test.pypi.org)")
    else:
        print("   🚀 Destination: Production PyPI (pypi.org)")

    if not ask_yes_no("Proceed with this release?"):
        print("❌ Release cancelled")
        return

    # Step 5: Update version files
    if not update_version_files(new_version):
        print("❌ Failed to update version files")
        sys.exit(1)

    # Step 6: Update changelog
    if not update_changelog(new_version, release_message):
        print("❌ Failed to update changelog")
        sys.exit(1)

    # Step 7: Handle git commits (skip entirely in test mode)
    if test_mode:
        print("🧪 TEST MODE: Skipping all git operations (no commits, no pushes)")
    else:
        if not ask_yes_no("Commit version changes to git?"):
            print("❌ Release cancelled")
            return

        # Commit changes - handle pre-commit hooks properly
        commit_message = f"🚀 RELEASE: v{new_version}\n\n{release_message}"

        # Try to commit with proper pre-commit hook handling
        max_retries = 3
        for attempt in range(max_retries):
            # Stage all changes before each attempt
            success, _ = run_command(
                "git add .", f"Staging changes (attempt {attempt + 1})"
            )
            if not success:
                print("❌ Failed to stage changes")
                sys.exit(1)

            # Try to commit
            success, output = run_command(
                f'git commit -m "{commit_message}"',
                f"Committing version changes (attempt {attempt + 1})",
            )

            if success:
                print("✅ Successfully committed changes")
                break

            # If this was the last attempt, fail
            if attempt == max_retries - 1:
                print("❌ Failed to commit changes after multiple attempts")
                print(f"📤 Last error output: {output}")
                sys.exit(1)

            # If pre-commit hooks modified files, the next iteration will re-stage them
            if "files were modified by this hook" in output:
                print(f"🔄 Pre-commit hooks modified files, will re-stage and retry...")
            else:
                print(
                    f"🔄 Commit failed, retrying... (attempt {attempt + 1}/{max_retries})"
                )

        # Step 8: Ask to push to GitHub
        if not ask_yes_no("Push changes to GitHub?"):
            print("❌ Skipping GitHub push")
        else:
            success, _ = run_command("git push origin main", "Pushing to GitHub")
            if not success:
                print("❌ Failed to push to GitHub")
                sys.exit(1)

    # Step 9: Ask to build package
    if not ask_yes_no("Build package for PyPI?"):
        print("❌ Skipping package build")
        return

    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/", "Cleaning previous builds")

    # Build package
    success, _ = run_command("python -m build", "Building package")
    if not success:
        print("❌ Failed to build package")
        sys.exit(1)

    # Step 10: Ask to upload to PyPI
    upload_destination = "Test PyPI" if test_mode else "PyPI"
    if not ask_yes_no(f"Upload to {upload_destination}?"):
        print(f"❌ Skipping {upload_destination} upload")
        print(f"✅ Release v{new_version} prepared successfully!")
        if test_mode:
            print(
                "🎯 To upload to Test PyPI later, run: twine upload --repository testpypi dist/*"
            )
        else:
            print("🎯 To upload later, run: twine upload dist/*")
        return

    # Upload to PyPI or Test PyPI
    if test_mode:
        upload_cmd = "twine upload --repository testpypi dist/*"
        upload_desc = "Uploading to Test PyPI"
    else:
        upload_cmd = "twine upload dist/*"
        upload_desc = "Uploading to PyPI"

    success, _ = run_command(upload_cmd, upload_desc, capture_output=False)
    if not success:
        print(f"❌ Failed to upload to {upload_destination}")
        sys.exit(1)

    print(f"\n🎉 Release v{new_version} completed successfully!")
    print("✅ Version updated")
    if not test_mode:
        print("✅ Changes committed and pushed to GitHub")
    if test_mode:
        print("✅ Package uploaded to Test PyPI")
        print("🔗 View at: https://test.pypi.org/project/langbase/")
        print(
            "🧪 Test install: pip install --index-url https://test.pypi.org/simple/ langbase"
        )
        print(
            "⚠️  Version files were updated locally but NOT committed - you may want to reset them!"
        )
        print(
            "💡 To reset: git checkout -- pyproject.toml langbase/__init__.py CHANGELOG.md"
        )
    else:
        print("✅ Package uploaded to PyPI")
        print("🔗 View at: https://pypi.org/project/langbase/")


if __name__ == "__main__":
    main()
