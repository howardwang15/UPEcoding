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
    return words_list, file


def get_words_same_length(state, words_array):
    possible_words = []
    for target in state:
        possibles = []
        for word in words_array:
            if len(target) == len(word):
                possibles.append(word)
        if len(possibles) == 0:
            print("can't find word with length {}".format(len(target)))
        possible_words.append(possibles)
    return possible_words


def find_possible_words(state, possibles):
    if len(possibles) != len(state):
        print("state: {}".format(state))
        print("possibles: {}".format(possibles))
        print("state length: {}".format(len(state)))
        print("possibles length: {}".format((len(possibles))))
        return [['Z']]
        #raise ValueError("cant fucking continue")

    possibles_new = [] #stores new possible words
    for i in range(len(state)): #go through all of the words in the state
        letter_dict = {} #letters found in current state
        for j in range(len(state[i])):
            if state[i][j] == '-' or state[i][j] == '(' or state[i][j] == ')' or state[i][j] == '?' or state[i][j] == '!': #ignore these special characterrs
                continue
            if state[i][j] != '_': #if not all underscores, then store char in dictionary (position, char)
                letter_dict[j] = state[i][j] #store the new letter into a dictionary for quick lookup time

        good_words = [] #stores possible words from the wordlist file corresponding to each word in the state
        if (len(possibles) == 0):
            print("no possibles!")
            continue

        if len(letter_dict) == 0:
            possibles_new.append(possibles[i]) #append the old possible words list
            print("added old words as new words: {}".format(j))
            continue

        print("length: {}".format(len(possibles)))
        for word in possibles[i]: #possibles[i] = all the words that might be at position i of state
            #print("possible word for state word {0} (length {1}): {2} (length {3})".format(state[i], len(state[i]), word, len(word)))
            matching_letters = 0
            #print("word: {0}, dict: {1}".format(word, letter_dict))
            for key, value in letter_dict.items():
                if word[key] == value:
                    matching_letters += 1

            if matching_letters == len(letter_dict): #all letters are in promising positions
                good_words.append(word)

        if len(good_words) == 0:
            print("no good words were found")
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

    return chr(frequencies.index(max(frequencies)) + 97), max(frequencies)


def get_remaining_letters(letters_used):
    return list(set(most_popular_letters) - set(letters_used))


def main():
    rounds_played = 0

    additional_words = []
    while rounds_played < 100: #initialization step
        words_list, file = init()
        data = requests.get(endpoint).json()
        state = data['state'].split()
        status = data['status']
        remaining_guesses = data['remaining_guesses']
        remaining_guesses_before_last_guess = remaining_guesses
        possible_words = get_words_same_length(state, words_list)
        for newly_found in additional_words:
            file.write(newly_found)
            file.write("\n")
        file.close()
        additional_words = []
        assert (len(possible_words) == len(state))
        for i in range(len(state)):
            for j in range(len(possible_words[i])):
                # print("state length: {0}, word length: {1}".format(len(state[i]), len(possible_words[i][j])))
                assert (len(possible_words[i][j]) == len(state[i]))


        used_letters = []
        char = 'e'
        hack = False
        while status == 'ALIVE':
            if hack:
                break
            response = requests.post(endpoint, data={'guess': char})
            data = response.json()
            state = data['state'].split()
            status = data['status']
            remaining_guesses = data['remaining_guesses']
            if remaining_guesses == remaining_guesses_before_last_guess:
                possible_words = find_possible_words(state, possible_words)
                if len(possible_words) != len(state) and len(possible_words) != 1:
                    print("what the actual fuck")
                if len(possible_words) != 0 and len(possible_words[0]) != 0 and possible_words[0][0] == 'Z':
                    print("error encountered")
                    break
            remaining_guesses_before_last_guess = remaining_guesses
            used_letters.append(char)
            special_case = False
            for words in possible_words:
                for word in words:
                    if len(word) == 1 or len(word) == 2 and 'a' not in used_letters: #hack for common 1-2 letter words
                        char = 'a'
                        special_case = True
                    elif len(word) == 1 or len(word) == 2 and 'i' not in used_letters:
                        char = 'i'
                        special_case = True
            if not special_case:
                char, frequency = get_most_frequent_letter(possible_words, used_letters)
                if remaining_guesses == 1 and frequency <= 2:
                    hack = True

        rounds_played += 1
        print("rounds_played: {}".format(rounds_played))
        if status == 'DEAD':
            for word in data['lyrics'].split():
                additional_words.append(word)

    print(data['win_rate'])


if __name__ == '__main__':
    main()