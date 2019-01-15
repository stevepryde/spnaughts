"""Insert bots into database."""

from typing import Any, Dict, List

from pymongo import MongoClient, ASCENDING, DESCENDING


class BotDB:
    """Bot Database."""

    def __init__(self) -> None:
        """Create a new BotDB object."""
        self.client = MongoClient()
        self.db = self.client.botdb
        self.db.bots.create_index([("name", ASCENDING)])
        self.db.bots.create_index([("name", ASCENDING), ("score", DESCENDING)])
        return

    def insert_bot(self, bot_name: str, bot_dict: Dict[str, Any], score: float) -> str:
        """Insert the specified bot dict into the db and return the id."""
        return self.db.bots.insert_one(
            {"name": bot_name, "bot": bot_dict, "score": score}
        ).inserted_id

    def load_bot(self, bot_id: str) -> Dict[str, Any]:
        """Get bot by id."""
        return self.db.bots.find_one({"_id": bot_id})

    def get_top(self, bot_name: str, count: int) -> List[Dict[str, Any]]:
        """Get top scoring bots."""
        return self.db.bots.find(filter={"name": bot_name}, sort={"score": -1}, limit=count)

    def clear_bots(self, bot_name: str) -> None:
        """Delete all bots with this name."""
        self.db.bots.delete_many({"name": bot_name})
        return

