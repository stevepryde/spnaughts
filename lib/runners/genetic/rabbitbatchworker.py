"""Batch Worker using rabbitmq."""

from typing import Any, Dict

from lib.batch import Batch
from lib.botfactory import BotFactory
from lib.gamecontext import GameContext


def run_one_batch(batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run one batch and return the output data."""
    context = GameContext()

    bots = []
    batch_config = batch_data.get("batch_config", {})
    bot_config = batch_config.get("bot_config", {})

    for bot_data in batch_data.get("bot_data", []):
        bot = BotFactory(context, bot_config=bot_config).create_bot(bot_data.get("name", ""))
        bot.from_dict(bot_data)
        bots.append(bot)

    batch = Batch(bots, batch_config)
    batch_result = batch.run_batch()

    genetic_index = batch_data.get("genetic_index", 0)
    genetic_identity = batch.identities[genetic_index]
    genetic_score = batch_result.get_score(genetic_identity)
    sample_index = batch_data.get("sample", 0)

    win = ""
    if genetic_score > batch_data.get("score_threshold", 0):
        win = "*"

    print(
        "Completed batch for sample {:5d} :: score = {:.3f} {}".format(
            batch_data.get("sample", 0), genetic_score, win
        )
    )

    return {
        "qid": batch_data.get("qid", "test"),
        "bot_data": batch.bots[genetic_index].to_dict(),
        "genetic_score": genetic_score,
        "sample": sample_index,
    }

