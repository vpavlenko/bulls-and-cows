#!/usr/bin/env python3

import re
from math import log
from copy import copy
from random import shuffle, randrange, seed


seed(42)

NUM_DIGITS = 4


def is_allowed_number(number):
    return len(str(number)) == NUM_DIGITS and len(set(str(number))) == NUM_DIGITS


ALL_NUMBERS = [number for number in range(1000, 10000) if is_allowed_number(number)]
POTENTIAL_ANSWERS = [(0, 1), (0, 2), (1, 1), (1, 0), (0, 0), (0, 3), (1, 2), (2, 0), (2, 1), (3, 0), (0, 4), (1, 3), (2, 2), (4, 0)]
# this order should accelerate the execution of question_entropy() 


def count_bulls_and_cows(number, question):
    number = str(number)
    question = str(question)
    bulls = 0
    cows = 0
    for i in range(NUM_DIGITS):
        for j in range(NUM_DIGITS):
            if number[i] == question[j]:
                if i == j:
                    bulls += 1
                else:
                    cows += 1
    return (bulls, cows)


def number_is_consistent_with_qa(number, question, answer):
    return count_bulls_and_cows(number, question) == answer


def count_possible_numbers(history, allowed_numbers):
    count = 0
    for number in allowed_numbers:
        if all(number_is_consistent_with_qa(number, question, answer) for question, answer in history):
            count += 1
    return count


def get_unique_possible_number(history):
    for number in ALL_NUMBERS:
        if all(number_is_consistent_with_qa(number, question, answer) for question, answer in history):
            return number


def question_entropy_by_history(history, allowed_numbers):
    current_min_entropy = 10 ** 9
    def question_entropy(question):
        nonlocal current_min_entropy
        result = 0
        for answer in POTENTIAL_ANSWERS:
            count = count_possible_numbers([(question, answer)], allowed_numbers)
            if count > 0:
                result += - log(1 / count) * count
                if result > current_min_entropy:
                    return result
        current_min_entropy = result
        return result
    return question_entropy


def get_best_question(step, history, current_allowed_numbers):
    if step > 1:
        for number in list(current_allowed_numbers):
            if not number_is_consistent_with_qa(number, *history[-1]):
                current_allowed_numbers.remove(number)

    sample = list(current_allowed_numbers)
    shuffle(sample)
    sample = sample[:10 ** (step - 1)]
    return min(sample, key=question_entropy_by_history(history, current_allowed_numbers))


class Game:
    def __init__(self):
        self.history = []
        self.i = 0
        self.current_allowed_numbers = set(ALL_NUMBERS)

    def is_finished(self):
        return count_possible_numbers(self.history, ALL_NUMBERS) <= 1

    def get_question(self):
        assert not self.is_finished()
        self.i += 1
        self.last_question = get_best_question(self.i, self.history, self.current_allowed_numbers)
        return self.last_question

    def put_answer(self, answer):
        assert len(answer) == 2
        self.history.append((self.last_question, answer))

    def get_step(self):
        if self.is_finished():
            return self.i if self.history[-1][1][0] == 4 else self.i + 1
        else:
            return self.i

    def is_correct(self):
        return count_possible_numbers(self.history, ALL_NUMBERS) > 0

    def guessed_number(self):
        return get_unique_possible_number(self.history)


def interactive_game():
    print("""This is 'Bulls and cows' solver
Author: Vitaly Pavlenko, http://vk.com/vitalypavlenko
Date: Nov 11 2012

Think of some number of four digits.  All digits should be different.
For every question please answer two numbers: bulls and cows.
Example: if your secret number is 1234 and my question is 1453, you should answer '1 2'.
""")
    game = Game()
    while not game.is_finished():
        question = game.get_question()
        print('Question #{0}: {1}'.format(game.get_step(), question))
        answer = tuple([int(i) for i in re.findall(r'[0-9]+', input())])  # should be a tuple of two numbers
        if len(answer) != 2:
            raise ValueError('your answer should contain exactly two numbers')
        game.put_answer(answer)
    if game.is_correct():
        print("Your number is {0}.  It took me {1} steps to guess it.".format(game.guessed_number(), game.get_step()))
    else:
        print("It seems that you've made a mistake somewhere.")


def test_all_numbers():
    worst_number_of_steps = 0
    for number in ALL_NUMBERS:
        print('Testing number {0}'.format(number))
        game = Game()
        while not game.is_finished():
            question = game.get_question()
            print('  Question #{0}: {1}'.format(game.get_step(), question))
            answer = count_bulls_and_cows(number, question)
            print('  Answer: {0}'.format(answer))
            game.put_answer(answer)
        assert game.is_correct()
        if game.get_step() > worst_number_of_steps:
            worst_number_of_steps = game.get_step()
        print('  Total number of steps:', game.get_step())
        print('  The worst one was:    ', worst_number_of_steps)


if __name__ == "__main__":
    interactive_game()
    # test_all_numbers()
