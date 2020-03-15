"""CS 61A Presents The Game of Hog."""

from dice import six_sided, four_sided, make_test_dice
from ucb import main, trace, interact

GOAL_SCORE = 100  # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################


def roll_dice(num_rolls, dice=six_sided):
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    count, total, roll_one = 0, 0, False
    while count < num_rolls:
        dice_outcome = dice()
        if dice_outcome == 1:
            roll_one = True
        else:
            total += dice_outcome
        count += 1
    if roll_one == True:
        return 1
    else:
        return total

def free_bacon(score):
    assert score < 100, 'The game should be over.'
    if (score // 10) - (score % 10) < 0: #if the tens digit minus the ones digit is negative
        return 2 + -1 * ((score // 10) - (score % 10)) #change the negative difference to a positive
    else:
        return 2 + (score // 10) - (score % 10)


def take_turn(num_rolls, opponent_score, dice=six_sided):
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice in take_turn.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    if num_rolls == 0: #if the player decides to do free bacon
        return free_bacon(opponent_score) #function returns free bacon score
    else:
        sum = roll_dice(num_rolls, dice) #finds the score by summing up the dice value from each roll
    return sum

def is_swap(score0, score1):
    if score0 <= 1: #swap will not happen if player0's score is 0 or 1
        return False
    elif score1 <= 1: #swap will not happen if player1's score is 0 or 1
        return False
    elif score0 % score1 == 0: #score 1 is a multiple of score0
        return True
    elif score1 % score0 == 0: #score 0 is a multiple of score1
        return True
    else:
        return False #no swap will happen

def other(player):
    return 1 - player

def silence(score0, score1):
    return silence

def play(strategy0, strategy1, score0=0, score1=0, dice=six_sided,
         goal=GOAL_SCORE, say=silence):
    player = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    while score0 < goal and score1 < goal:
        if player == 0: #Player 0 is rolling
            score, opponent_score, strategy, opponent_strategy = score0, score1, strategy0, strategy1
            num_rolls = strategy(score, opponent_score)
            count = take_turn(num_rolls, opponent_score, dice)
            if count == 0:
                opponent_score += num_rolls
            else:
                score += count
            if is_swap(score, opponent_score) == True:
                score, opponent_score = opponent_score, score
            if score0 >= goal or score1 >= goal:
                return score0, score1
            score0, score1, strategy0, strategy1 = score, opponent_score, strategy, opponent_strategy
        else: #Player 1 is rolling
            score, opponent_score, strategy, opponent_strategy = score1, score0, strategy1, strategy0
            num_rolls = strategy(score, opponent_score)
            count = take_turn(num_rolls, opponent_score, dice)
            if count == 0:
                opponent_score += num_rolls
            else:
                score += count
            if is_swap(score, opponent_score) == True:
                score, opponent_score = opponent_score, score
            if score0 >= goal or score1 >= goal:
                return score0, score1
            score1, score0, strategy1, strategy0 = score, opponent_score, strategy, opponent_strategy
        player = other(player)
        say = say(score0, score1)
    return score0, score1


#######################
# Phase 2: Commentary #
#######################


def say_scores(score0, score1):
    """A commentary function that announces the score for each player."""
    print("Player 0 now has", score0, "and Player 1 now has", score1)
    return say_scores

def announce_lead_changes(previous_leader=None):
    def say(score0, score1):
        if score0 > score1:
            leader = 0
        elif score1 > score0:
            leader = 1
        else:
            leader = None
        if leader != None and leader != previous_leader:
            print('Player', leader, 'takes the lead by', abs(score0 - score1))
        return announce_lead_changes(leader)
    return say

def both(f, g):
    def say(score0, score1):
        return both(f(score0, score1), g(score0, score1))
    return say


def announce_highest(who, previous_high=0, previous_score=0):
    assert who == 0 or who == 1, 'The who argument should indicate a player.'
    def say(score0, score1):
        if who == 0: #assigning player0 to score
            score = score0
        else:
            score = score1 #assigning player1 to score
        difference = score - previous_score
        if difference > previous_high:
            if difference == 1: #if the difference is 1, point needs to be singular
                print(difference, "point! That's the biggest gain yet for Player", who)
                return announce_highest(who, previous_high=difference, previous_score=score)
            else: #any other difference will have points
                print(difference, "points! That's the biggest gain yet for Player", who)
                return announce_highest(who, previous_high=difference, previous_score=score)
        else: #the score gain did not result in a record
            return announce_highest(who, previous_high=previous_high, previous_score=score)
    return say


#######################
# Phase 3: Strategies #
#######################

def always_roll(n):
    def strategy(score, opponent_score):
        return n
    return strategy

def make_averaged(fn, num_samples=1000):
    def print_make_averaged(*args):
        sample_count = 0 #records the number of samples
        sample_sum = 0 #records the sum of the samples
        while sample_count < num_samples:
            sample_result = fn(*args)
            sample_sum += sample_result
            sample_count += 1
        return (sample_sum / num_samples)
    return print_make_averaged

def max_scoring_num_rolls(dice=six_sided, num_samples=1000):
    i, max_avg, max_dice, avg_func = 1, 0, 0, make_averaged(roll_dice, num_samples)
    while i <= 10:
        dice_avg = avg_func(i, dice)
        if dice_avg > max_avg:
            max_avg, max_dice = dice_avg, i
        i += 1
    return max_dice


def winner(strategy0, strategy1):
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1


def average_win_rate(strategy, baseline=always_roll(4)):
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2


def run_experiments():
    if False:  # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)

    if True:  # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if True:  # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if True:  # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True:  # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"


def bacon_strategy(score, opponent_score, margin=8, num_rolls=4):
    if free_bacon(opponent_score) < margin:
        return num_rolls
    elif free_bacon(opponent_score) >= margin:
        return 0


def swap_strategy(score, opponent_score, margin=8, num_rolls=4):
    if opponent_score % (score + free_bacon(opponent_score)) == 0:
        return 0
    elif free_bacon(opponent_score) < margin:
        return num_rolls
    elif free_bacon(opponent_score) >= margin:
        return 0

def final_strategy(score, opponent_score):
    return 4


##########################
# Command Line Interface #
##########################

# NOTE: Functions in this section do not need to be changed. They use features
# of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')

    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()
