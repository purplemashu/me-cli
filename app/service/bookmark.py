import os
import json
from typing import List, Dict

class Bookmark:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.packages: List[Dict] = []
            self.filepath = "bookmark.json"

            if os.path.exists(self.filepath):
                self.load_bookmark()
            else:
                self._save([])  # create empty file

            self._initialized = True

    def _save(self, data: List[Dict]):
        """Helper to write JSON safely."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _ensure_schema(self):
        """Ensure all bookmarks have the latest schema fields."""
        updated = False
        for p in self.packages:
            if "family_name" not in p:  # add missing field
                p["family_name"] = ""
                updated = True
            if "order" not in p:
                p["order"] = 0
                updated = True
        if updated:
            self.save_bookmark()  # persist schema upgrade

    def load_bookmark(self):
        """Load bookmarks from JSON file and ensure schema consistency."""
        with open(self.filepath, "r", encoding="utf-8") as f:
            self.packages = json.load(f)
        self._ensure_schema()

    def save_bookmark(self):
        """Save current bookmarks to JSON file."""
        self._save(self.packages)

    def add_bookmark(
        self,
        family_code: str,
        family_name: str,
        is_enterprise: bool,
        variant_name: str,
        option_name: str,
        order: int,
    ) -> bool:
        """Add a bookmark if it does not already exist."""
        key = (family_code, variant_name, order)

        if any(
            (p["family_code"], p["variant_name"], p["order"]) == key
            for p in self.packages
        ):
            print("Bookmark already exists.")
            return False

        self.packages.append(
            {
                "family_name": family_name,  # required field
                "family_code": family_code,
                "is_enterprise": is_enterprise,
                "variant_name": variant_name,
                "option_name": option_name,
                "order": order,
            }
        )
        self.save_bookmark()
        print("Bookmark added.")
        return True

    def remove_bookmark(
        self,
        family_code: str,
        is_enterprise: bool,
        variant_name: str,
        order: int,
    ) -> bool:
        """Remove a bookmark if it exists. Returns True if removed."""
        for i, p in enumerate(self.packages):
            if (
                p["family_code"] == family_code
                and p["is_enterprise"] == is_enterprise
                and p["variant_name"] == variant_name
                and p["order"] == order
            ):
                del self.packages[i]
                self.save_bookmark()
                print("Bookmark removed.")
                return True
        print("Bookmark not found.")
        return False

    def get_bookmarks(self) -> List[Dict]:
        """Return all bookmarks."""
        return self.packages.copy()

BookmarkInstance = Bookmark()
