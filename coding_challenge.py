import numpy as np
import json
import requests
import time

endpoint = 'http://upe.42069.fun/v5J8d'
words_path = "words.txt"

letters = "ESIARNTOLCDUPMGHBYFVKWZXQJ" #http://datagenetics.com/blog/april12012/index.html
letters = letters.lower()
most_popular_letters = list(letters)

def init():
    file = open(words_path)
    words_list = [line.strip('\n') for line in file]
    return words_list


def get_words_same_length(state, words_array):
    possible_words = []
    for target in state:
        possibles = []
        for word in words_array:
            if len(target) == len(word):
                possibles.append(word)
        possible_words.append(possibles)
    return possible_words


def find_possible_words(state, possibles):
    possibles_new = []
    for i in range(len(state)): #go through all of the words in the state
        letter_dict = {} #good letters
        for j in range(len(state[i])):
            if state[i][j] != '_': #if not all underscores, then store char in dictionary (position, char)
                letter_dict[j] = state[i][j]

        good_words = [] #stores possible words corresponding to each word in the state
        if (len(possibles) == 0):
            print("no possibles!")
            continue

        if len(letter_dict) == 0:
            continue

        for word in possibles[i]: #possibles[i] = all th words that might be at position i of state
            print("possible word for state word {0} (length {1}): {2} (length {3})".format(state[i], len(state[i]), word, len(word)))
            matching_letters = 0
            for key, value in letter_dict.items():
                if word[key] == value:
                    matching_letters += 1

            if matching_letters == len(letter_dict): #all letters are in promising positions
                print(word)
                good_words.append(word)

        if len(good_words) != 0:
            possibles_new.append(good_words)
    return possibles_new


def get_most_frequent_letter(words, used_letters):
    frequencies = [0]*26

    for i in range(len(words)):
        for word in words[i]:
            for letter in word:
                already_used = False
                for used in used_letters:
                    if letter == used:
                        already_used = True
                        break
                if not already_used:
                    frequencies[ord(letter) - 97] += 1

    return chr(frequencies.index(max(frequencies)) + 97)


def get_remaining_letters(letters_used):
    return list(set(most_popular_letters) - set(letters_used))


for words in possible_words:
    for word in words:
        if len(word) == 1 or len(word) == 2 && 'a' not in used_letters:
            char = 'a'
        else if len(word) == 1 or len(word) == 2 && 'i' not in used_letters:
            char = 'i'

def main():
    words_list = init()

    rounds_played = 0

    while rounds_played < 100: #initialization step
        data = requests.get(endpoint).json()
        state = data['state'].split()
        status = data['status']
        remaining_guesses = data['remaining_guesses']
        remaining_guesses_before_last_guess = remaining_guesses
        possible_words = get_words_same_length(state, words_list)
        assert (len(possible_words) == len(state))
        for i in range(len(state)):
            for j in range(len(possible_words[i])):
                # print("state length: {0}, word length: {1}".format(len(state[i]), len(possible_words[i][j])))
                assert (len(possible_words[i][j]) == len(state[i]))


        used_letters = []
        char = 'e'
        while status == 'ALIVE':
            response = requests.post(endpoint, data={'guess': char})
            data = response.json()
            state = data['state'].split()
            status = data['status']
            remaining_guesses = data['remaining_guesses']
            if remaining_guesses == remaining_guesses_before_last_guess:
                possible_words = find_possible_words(state, possible_words)
                print("number of possible words in array: {}".format(len(possible_words)))
                print("possible words: {}".format(possible_words))
            remaining_guesses_before_last_guess = remaining_guesses
            used_letters.append(char)
            char = get_most_frequent_letter(possible_words, used_letters)

        rounds_played += 1
        print(data['lyrics'])

    print(data['win_rate'])


if __name__ == '__main__':
    main()