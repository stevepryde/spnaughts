"""Batch Worker using rabbitmq."""

import json

from lib.batch import Batch
from lib.botfactory import BotFactory
from lib.gamecontext import GameContext
from .rabbit import QUEUE_START, QUEUE_STOP, rabbit


def rabbit_batchworker(ch, method, properties, body):
    """Worker for a single rabbit job."""
    context = GameContext()

    try:
        batch_data = json.loads(body)
    except ValueError:
        if method:
            rabbit.done_message(method.delivery_tag)
        return

    print("batch_data = {}".format(batch_data))

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

    win = ""
    if genetic_score > batch_data.get("score_threshold", 0):
        win = "*"

    print(
        "Completed batch for sample {:5d} :: score = {:.3f} {}".format(
            batch_data.get("sample", 0), genetic_score, win
        )
    )

    rabbit.put_on_queue(
        QUEUE_STOP,
        {"bot_data": batch.bots[genetic_index].to_dict(), "genetic_score": genetic_score},
    )
    rabbit.done_message(method.delivery_tag)
    return
