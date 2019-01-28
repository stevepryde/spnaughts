# NAUGHTS AND CROSSES AI EXPERIMENT

SP Naughts is a simple naughts and crosses "game" including a collection of
AI bots.

It is intended to be a sandbox for testing AI / machine learning algorithms.
Only naughts and crosses is implemented for now, but additional games will be
added in future, for example connect 4.

## Run games using game_runner.py:

    $ ./game_runner.py -h
    usage: game_runner.py [-h] --game GAME [--batch BATCH] [--genetic GENETIC]
                      [--samples SAMPLES] [--keep KEEP] [--botid BOTID]
                      bot1 bot2

    Game Runner

    positional arguments:
      bot1               First bot, e.g. "human"
      bot2               Second bot

    optional arguments:
      -h, --help         show this help message and exit
      --game GAME        The game to run
      --batch BATCH      Batch mode. Specify the number of games to run
      --genetic GENETIC  Genetic mode. Specify number of generations to run
                        (Requires --batch)
      --samples SAMPLES  Number of samples per generation. (Requires --genetic)
      --keep KEEP        Number of winning samples to "keep" (Requires --genetic)
      --botid BOTID      Play against this bot id (genetic)

You need to specify two robots, along with some additional arguments.

The robot names are simply the directory names of the bots.
Game-specific bots can be found in games/naughts/bots/.
Game-agnostic bots can be found in bots/.

The first bot specified is always X, and will make the first move.

## SINGLE MODE

For example:

    $ ./game_runner.py --game naughts randombot naughts.human

This will run a single game where randombot plays against a human player.

NOTE: Because the human 'bot' receives input from STDIN, it is not practical
to run the human player in anything other than single game mode.

Game log files are output into the logs/ directory. This directory will be
created if it does not exist. Logging is quite minimal at the moment,
although logging functionality is supported and ready to use by games.

## BATCH MODE

Use the --batch option to run a batch of games in a row.

For example:

    $ ./game_runner.py randombot naughts.simplebot --game naughts --batch 1000

This will run a batch of 1000 games and then output a summary at the end.

## GENETIC MODE

This is the mode used to run bots based on a genetic algorithm.

For example:

    $ ./game_runner.py randombot naughts.genbot1 --game naughts --batch 100 --samples 50 --genetic 10

This will run the randombot (as 'X') against the genbot1 (as 'O'), over 10
generations. Each generation will have 50 samples. Each 'sample' will execute
a batch of 100 games before receiving an overall score (the average). The
highest scoring sample will be selected and another 50 samples generated
(or mutated) from that winning sample. This is the second generation.
If no sample scores higher than the previous generation, the samples are
regenerated from the previous generation's winner and the process is repeated.
At present this can result in never-ending games, so it pays to know what you're
looking for.

If two genetic bots are specified, only the first will have the genetic algorithm
applied to it. The other will behave as a static bot, unchanged from one game
to the next.

Top-scoring bots will be saved to a mongoDB instance if one is available, and can
be retrieved and replayed using the --botid command-line option.

## ROBOTS

The interesting 'bots' included are as follows:

### Game-independent bots (these will run against future games unmodified)

- randombot
  Just chooses from the available moves at random. Very useful for training
  or testing other bots (in batch mode or genetic mode).
- nbot1
  My first attempt at a neural network. There is no back-propagation since
  it uses a genetic algorithm instead to mutate it over time. This is obviously
  much less efficient but requires far less knowledge of the game being
  "learned". The code is intentionally verbose to make it easier to read.
  Once it is working it can be optimised for performance using numpy.

### Game-dependent bots (these will only run against naughts)

- human
  This one accepts input from STDIN, allowing you to play manual games against
  any other bot.
- perfectbot
  This was my first attempt at creating a bot that would never lose, based on
  simple intuitive rules.
- minimaxbot
  A bot that uses the minimax algorithm (with alpha-beta optimisation). This
  will always produce the optimal outcome, and is thus useful for benchmarking
  other bots.
- genbot1
  My first attempt at a genetic algorithm. It uses boolean logic nodes
  assembled at random. See the documentation in the python source file for
  a more detailed explanation of how it works.
- genbotcontrol
  Designed to appear identical to genbot1 but with the central logic replaced
  by simple random move selection. This is used to compare against genbot1 to
  check that any improvement seen in genbot1 is actually real.
- genbot2
  This bot uses the same algorithm as genbot1, but without any additional rules
  or extra logic. Whereas genbot1 included specific hard-coded rules to
  automatically choose a winning or defensive move if one was available,
  genbot2 does not, and it is entirely driven by the AI. As you might expect,
  this makes it comparable to randombot in its initial state, but with the
  right training it should be able to improve considerably. How much improvement
  is possible is still yet to be determined.
- omnibot
  Omnibot is a special bot that, when combined with a magic batch runner,
  effectively produced a kind of british-museum algorithm for running every
  possible game against a bot. At each turn, the board is cloned once for
  every possible move, and the clones added to a stack. When the stack has
  been fully processed, every possible game has been played.
  Omnibot was deleted due to a recent refactor but the functionality it
  provided will return in a future update.

## FUTURE

This project has recently undergone a major refactor to hopefully allow much
more future expansion.

Batches should now be much less dependent on bulky objects, to make way for
better parallelism. I'd like to try pushing batches onto a queue and then
processing them from a pool of machines, ideally docker containers. This will
significantly improve processing performance and allow much larger sample
sizes.

Omnibot has been temporarily removed, but its functionality will be restored
in a future update.

Once I have a nice neural net bot that can learn and self-improve, the longer
term goal is to implement more games. Connect four will be the obvious next
choice. Nbot1 and randombot are now fully generic so hopefully they will work
against future games without any modification to their code.

That's all for now.

I hope you enjoy it.
