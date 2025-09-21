import os
from typing import List, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

class IsAdmin(BaseFilter):
    """
    A filter to check if a user is an admin.
    Admins are identified by their Telegram User ID, which are stored
    in the .env file as a comma-separated string.
    """
    def __init__(self):
        self.admin_ids = self._get_admin_ids()

    def _get_admin_ids(self) -> List[int]:
        """Loads admin IDs from environment variables."""
        admin_ids_str = os.getenv("ADMIN_IDS")
        if not admin_ids_str:
            return []
        try:
            return [int(admin_id.strip()) for admin_id in admin_ids_str.split(',')]
        except ValueError:
            # Handle cases where the ID is not a valid integer
            print("Warning: Could not parse one or more ADMIN_IDS. Please ensure they are comma-separated integers.")
            return []

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """
        This method is called every time the filter is checked.
        It returns True if the user is an admin, False otherwise.
        """
        # In `aiogram 3.x`, the `from_user` attribute is consistent
        # across Messages and CallbackQueries.
        user_id = event.from_user.id
        return user_id in self.admin_ids
