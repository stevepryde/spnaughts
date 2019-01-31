"""Start the rabbit worker."""

from lib.runners.genetic.rabbit import QUEUE_START, rabbit
from lib.runners.genetic.rabbitbatchworker import rabbit_batchworker

if __name__ == "__main__":
    print("Starting Rabbit Worker...")
    try:
        rabbit.consume_queue(QUEUE_START, rabbit_batchworker)
    except KeyboardInterrupt:
        print("Cancelled.")
