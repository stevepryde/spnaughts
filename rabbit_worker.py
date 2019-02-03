"""Start the rabbit worker."""

import json
import multiprocessing
import os
import sys
import time

from lib.runners.genetic.rabbit import RabbitDisabledError, RabbitManager
from lib.runners.genetic.rabbitbatchworker import run_one_batch


def consume():
    print("Connecting to rabbit...")
    try:
        rabbit = RabbitManager(
            host=os.environ.get("SPNAUGHTS_RABBIT"),
            username=os.environ.get("SPNAUGHTS_USERNAME"),
            password=os.environ.get("SPNAUGHTS_PASSWORD"),
        )
    except RabbitDisabledError:
        print("ERROR: Rabbit connection failed")
        return

    if not rabbit.enabled:
        print("ERROR: Rabbit connection failed: {}".format(rabbit.error))
        return
    print("Rabbit connected at {}".format(rabbit.host))

    def rabbit_process_job(ch, method, properties, body):
        """Worker for a single rabbit job."""
        try:
            batch_data = json.loads(body)
        except ValueError:
            if method:
                rabbit.done_message(method.delivery_tag)
            return

        batch_result = run_one_batch(batch_data)

        rabbit.put_on_output_exchange(qid=batch_result.get("qid", "test"), body=batch_result)
        rabbit.done_message(method.delivery_tag)
        return

    try:
        rabbit.consume_batch_queue(rabbit_process_job)
    except KeyboardInterrupt:
        print("Cancelled.")


if __name__ == "__main__":
    print("Starting Rabbit Workers...")
    try:
        num_workers = int(sys.argv[1])
    except ValueError:
        print("Usage: {} <num_workers>".format(sys.argv[0]))
        sys.exit(1)
    except (IndexError, KeyError):
        try:
            num_workers = int(os.environ["SPNAUGHTS_WORKERS"])
        except (ValueError, KeyError):
            num_workers = multiprocessing.cpu_count() - 2

    if num_workers > multiprocessing.cpu_count() - 1:
        num_workers = multiprocessing.cpu_count() - 1

    if num_workers < 1:
        num_workers = 1

    print("Workers: {}".format(num_workers))
    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=consume)
        p.start()
        processes.append(p)

    try:
        # Wait for workers to exit (i.e. on failure)
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Cancelled.")
        for p in processes:
            p.terminate()
