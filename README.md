# NAUGHTS AND CROSSES AI EXPERIMENT

SP Naughts is a simple naughts and crosses "game" including a collection of
AI bots.

It is intended to be a sandbox for testing AI / machine learning algorithms.

Currently supported games are:

1. Naughts and Crosses (Tic Tac Toe)
1. Connect Four

## Run games using game_runner.py:

    $ ./game_runner.py -h
    usage: game_runner.py [-h] --game GAME [--batch BATCH] [--magic]
                      [--genetic GENETIC] [--samples SAMPLES] [--keep KEEP]
                      [--wild WILD] [--botdb] [--botid BOTID] [--rabbit]
                      bot1 bot2

    Game Runner

    positional arguments:
      bot1               First bot, e.g. "human"
      bot2               Second bot

    optional arguments:
      -h, --help         show this help message and exit
      --game GAME        The game to run
      --batch BATCH      Batch mode. Specify the number of games to run
      --magic            Magic Batch mode. Run all possible games against this
                        bot.
      --genetic GENETIC  Genetic mode. Specify number of generations to run
                        (Requires --batch)
      --samples SAMPLES  Number of samples per generation. (Requires --genetic)
      --keep KEEP        Number of winning samples to "keep" (Requires --genetic)
      --wild WILD        Number of "wild" (fresh, randomly generated) samples to
                        include in each generation
      --botdb            Enable storing and loading bots with BotDB
      --botid BOTID      Play against this bot id (genetic)
      --rabbit           Use the RabbitMQ processor

You need to specify two robots, along with some additional arguments.

The robot names are simply the directory names of the bots.
Game-specific bots can be found in games/naughts/bots/.
Game-agnostic bots can be found in bots/.

The first bot specified is always X, and will make the first move.

## SINGLE MODE

For example:

    $ ./game_runner.py --game naughts randombot naughts.human

This will run a single naughts game where randombot plays against a human player.

NOTE: Because the human 'bot' receives input from STDIN, it is not practical
to run the human player in anything other than single game mode.

Game log files are output into the logs/ directory. This directory will be
created if it does not exist. Logging is quite minimal at the moment,
although logging functionality is supported and ready to use by games
for debugging purposes.

## BATCH MODE

Use the --batch option to run a batch of games in a row.

For example:

    $ ./game_runner.py randombot naughts.simplebot --game naughts --batch 1000

This will run a batch of 1000 games and then output a summary at the end.

## GENETIC MODE

This is the mode used to run bots based on a genetic algorithm.

For example:

    $ ./game_runner.py randombot naughts.genbot2 --game naughts --batch 100 --samples 50 --genetic 10

This will run the randombot (as 'X') against the genbot2 (as 'O'), over 10
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

- randombot :: Just chooses from the available moves at random. Very useful for training
  or testing other bots (in batch mode or genetic mode). This will be especially useful for
  training bots where the number of possible games is far too large for omnibot to be practical.
- genbot3 :: The generic version of genbot2. This bot uses my own algorithm, which can be
  loosely described as a machine made from randomly assembled logic gates/nodes. Mutation involves
  replacing a random node with a new one, or simply choosing new random inputs for an existing node.
- nbot1 :: My first attempt at a neural network. There is no back-propagation since
  it uses a genetic algorithm instead to mutate it over time. This is obviously
  much less efficient but requires far less knowledge of the game being
  "learned". The code is intentionally verbose to make it easier to read.
  Once it is working it can be optimised for performance using numpy.

### Game-dependent bots (these will only run against naughts)

- human :: This one accepts input from STDIN, allowing you to play manual games against
  any other bot.
- perfectbot :: This was my first attempt at creating a bot that would never lose, based on
  simple intuitive rules.
- minimaxbot :: A bot that uses the minimax algorithm (with alpha-beta optimisation). This
  will always produce the optimal outcome, and is thus useful for benchmarking
  other bots.
- genbot1 :: My first attempt at a genetic algorithm. It uses boolean logic nodes
  assembled at random. See the documentation in the python source file for
  a more detailed explanation of how it works.
- genbotcontrol :: Designed to appear identical to genbot1 but with the central logic replaced
  by simple random move selection. This is used to compare against genbot1 to
  check that any improvement seen in genbot1 is actually real.
- genbot2 :: This bot uses the same algorithm as genbot1, but without any additional rules
  or extra logic. Whereas genbot1 included specific hard-coded rules to
  automatically choose a winning or defensive move if one was available,
  genbot2 does not, and it is entirely driven by the AI. As you might expect,
  this makes it comparable to randombot in its initial state, but with the
  right training it should be able to improve considerably. This bot has been
  demonstrated to be capable of learning.
- omnibot :: Omnibot is a special bot that, when combined with a magic batch runner,
  effectively produced a kind of british-museum algorithm for running every
  possible game against a bot. At each turn, the board is cloned once for
  every possible move, and the clones added to a stack. When the stack has
  been fully processed, every possible game has been played. This is the
  best bot to use for training genetic bots, as it is fully deterministic.

## TRAINING BOTS

Currently the ideal way to train bots is to run them against the omnibot using
the --magic option. Note that this is only practical for games with a very small
number of possible moves, such as naughts and crosses. For other games, it is
recommended to use randombot for now.

The below command-line has produced a GenBot2 sample capable of winning against
a randombot over 95% of the time, sometimes with 0 losses.

For comparison, minimaxbot (the optimal algorithm) wins against randombot roughly
99% of the time, always with 0 losses.

    ./game_runner.py naughts.genbot2 omnibot --game naughts --magic --genetic 500 --samples 10 --keep 2 --wild 5 --botdb

Let's look at the options used.

- We are running the naughts.genbot2 against the generic omnibot.
- --game naughts = Run the 'naughts and crosses' game. Currently this is the only game supported,
  but others will be added in future.
- --magic = Use the magic batch runner, which will play the genetic bot (in this case genbot2)
  against every possible move.
- --genetic 500 = Use the genetic algorithm runner for 500 generations.
- --samples 10 = Generate 10 random samples for every sample we "keep". Actually it will keep the
  winning samples and generate 9 random samples from each of them.
- --keep 2 = Keep the 2 highest scoring samples from each generation.
- --wild 5 = Add 5 "wild-card" (new, randomly generated) samples in each generation. This offers
  some protection against reaching local maxima.
- --botdb = If MongoDB is running, store the best bot recipes for replaying later. Always use
  this option unless you are sure you don't want to keep any of the generated bots.

The scoring system is arbitrary and will differ per game. Currently, naughts and crosses is
scored as follows:

- If you win, your score is 10 - number of turns.
- If you draw, your score is 0 (NOTE: the number of turns is always the same for a draw)
- If you lose, your score is 10 - number of turns, multiplied by -10.

Note that losses are weighted 10x as heavily as wins, because minimizing the number of losses is
a higher priority than maximizing the number of wins.

## FUTURE

This project has recently undergone a major refactor to hopefully allow much
more future expansion.

Connect Four is now implemented, including a human interface.

I would like to implement further games. The type of games that work well for now are
two-player, turn-based games with a fixed number of inputs and outputs per move.

I would like to put the games themselves online in the future, to allow
anyone to play against the bots that are in training.

I am considering a full rewrite in a faster language. Candidates include Javascript, Go and Kotlin.
Each has pros and cons, both for ease/speed of development and execute performance.

That's all for now.

I hope you enjoy it.
