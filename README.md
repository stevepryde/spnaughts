# NAUGHTS AND CROSSES AI EXPERIMENT

SP Naughts is a simple naughts and crosses "game" including a collection of
AI bots.

It is a WIP and about to receive a major overhaul.

## Run games using game_runner.py:

    $ ./game_runner.py -h
    usage: game_runner.py [-h] [--batch BATCH] [--stoponloss STOPONLOSS]
                          [--genetic GENETIC] [--samples SAMPLES] [--keep KEEP]
                          [--custom CUSTOM] [--loggames]
                          robot1 robot2

    Game Runner

    positional arguments:
      robot1                First robot, e.g. "human"
      robot2                Second robot

    optional arguments:
      -h, --help            show this help message and exit
      --batch BATCH         Batch mode. Specify the number of games to run
      --stoponloss STOPONLOSS
                            Stop if the specified player loses
      --genetic GENETIC     Genetic mode. Specify number of generations to run
                            (Requires --batch)
      --samples SAMPLES     Number of samples per generation. (Requires --genetic)
      --keep KEEP           Number of winning samples to "keep" (Requires
                            --genetic)
      --custom CUSTOM       Custom argument (passed to bot)
      --loggames            Also log individual games (may require a lot of disk
                            space!)

You need to specify two robots, followed by optional arguments.

The robot names are simply the directory names of the robots. Look in the
robots/ directory to find them.

The first robot is always X, and will make the first move.

## SINGLE MODE

For example:

    $ ./game_runner.py randombot human

This will run a single game where randombot plays against a human player.

NOTE: Because the human 'bot' receives input from STDIN, it is not practical
to run the human player in anything other than single game mode.

Game log files are output into the logs/ directory. This directory will be
created if it does not exist.

## BATCH MODE

Use the --batch option to run a batch of games in a row.

For example:

    $ ./game_runner.py randombot simplebot --batch 1000

This will run a batch of 1000 games and then output a summary at the end.

## GENETIC MODE

This is the mode used to run bots based on a genetic algorithm. One and only
one of the bots must be a genetic bot to run in this mode.

For example:

    $ ./game_runner.py randombot genbot1 --batch 1000 --samples 50 --genetic 10

This will run the randombot (as 'X') against the genbot1 (as 'O'), over 10
generations. Each generation will have 50 samples. Each 'sample' will execute
a batch of 1000 games before receiving an overall score (the average). The
highest scoring sample will be selected and another 50 samples generated
(or mutated) from that winning sample. This is the second generation.
If no sample scores higher than the previous generation, the samples are
regenerated from the previous generation's winner and the process is repeated.
At present this can result in never-ending games, so it pays to know what you're
looking for.

All game logs are output in logs/games/, including genetic bot 'recipes'.

To run a single game or batch against a particular recipe or to start a genetic
mode run from an existing recipe, simply copy the recipe from the relevant log
and paste it into its own file. Then supply that file on the CLI as follows:

    $ ./game_runner.py randombot genbot1 --batch 1000 --custom recipefile:/path/to/file

This will run a batch of 1000 games with randombot against a genbot1 that is
loaded from the particular recipe that has been supplied.

## ROBOTS

The interesting 'bots' included are as follows:

- randombot
  Just chooses from the available moves at random. Very useful for training
  or testing other bots (in batch mode or genetic mode).
- human
  This one accepts input from STDIN, allowing you to play manual games against
  any other bot.
- perfectbot
  This was my first attempt at creating a bot that would never lose, based on
  simple intuitive rules.
- minimaxbot
  A bot that uses the minimax algorithm (with alpha-beta optimisation). This
  will always produce the optimal outcome, and is thus useful for testing
  and training other bots.
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
  Perhaps the most important bot for AI training purposes. This bot will cover
  every possible path, when used with the new --batch=0 option. It basically
  just returns every possible move as a list, which tells the batch runner to
  clone the current game, spawning a 'new' game (with the current game state)
  for each available move. The number of games in the batch is the total number
  of possible games, which is dependent on the other bot (some games may always
  end early).

There are a couple of other bots included as well, that I used for testing.
See the documentation at the top of each source file for more details.

## FUTURE

This software has gotten more complicated than I'd like. The decision to put
all major objects inside a GameContext was intended to automatically set up
subdirectories and logging where appropriate, but it also added complexity.

The software is due for a design overhaul on the engine side of things.

First, the setup needs a shuffle. I think at the very top layer should be
the game object, and the bots themselves, or at least factories of them.
Currently the game object is instantiated inside the runner or batch, which
feels weird, and too deep in the guts of what is going on.

The game object and bots should be created up front, and then be supplied to
the particular runner, which just executes the game in a generic way.

To do this, there needs to be a separation between the game instance data / state,
and the game logic. The top level game object could be a game instance factory
that can dish up new clean game / data instances.

Aside from all of this, the actual batch processing currently touches far too
much code. I'm hitting performance bottlenecks trying to process batches, so
in order to improve performance the obvious option is to parallelise things.
But this requires moving batch processing into other processes and eventually
even other machines. In order to do that, batches need to be much leaner in
terms of what info they need passed in, and what they send back.

Then once it goes fully parallel, there is the discussion of how to move batch
info back and forth between the server and the workers. One option is a queue
such as rabbitmq. Another is websockets. Some experimentation will be required.

In terms of games, nbot1 is an early neural net approach, which is showing
some promise but really needs to run for many more generations to reach its
potential. Thus the performance focus.

Once I have a nice neural net bot that can learn and self-improve, the longer
term goal is to implement more games. Connect four will be the obvious next
choice. Ideally the game interface will be adjusted so that the inputs and
outputs can be more generic, and thus the neural net bot can be made somewhat
generic too. So long as we have inputs, outputs, and a score (fitness function),
it should just work. Fingers crossed.

That's all for now.

I hope you enjoy it.
