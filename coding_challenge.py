import numpy as np
import json
import requests
import time

endpoint = 'http://upe.42069.fun/v5J8d'
words_path = "words.txt"

letters = "ESIARNTOLDUYPMCGHBFKWVZXQJ" #http://datagenetics.com/blog/april12012/index.html
letters = letters.lower()
most_popular_letters = list(letters)

def init():
    file = open(words_path, 'r')
    words_list = [line.strip('\n') for line in file]
    file.close()
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
            #print("added old words as new words: {}".format(possibles[i]))
            continue

        #print("length: {}".format(len(possibles)))
        for word in possibles[i]: #possibles[i] = all the words that might be at position i of state
            #print("possible word for state word {0} (length {1}): {2} (length {3})".format(state[i], len(state[i]), word, len(word)))
            matching_letters = 0
            #print("word: {0}, dict: {1}".format(word, letter_dict))
            for key, value in letter_dict.items():
                if word[key] == value:
                    matching_letters += 1

            if matching_letters == len(letter_dict): #all letters are in promising positions
                good_words.append(word)


        possibles_new.append(good_words)

    return possibles_new


def get_most_frequent_letter(words, used_letters):
    frequencies = [0]*26
    #print("used in get fnc: {}".format(used_letters))
    for i in range(len(words)):
        for word in words[i]:
            #print("cur word: {}".format(word))
            for letter in word:
                already_used = False
                for used in used_letters:
                    if letter == used or letter == '\'':
                        already_used = True
                        break
                if not already_used:
                    frequencies[ord(letter) - 97] += 1
    #print(frequencies)
    if max(frequencies) == 0:
        for popular_letters in most_popular_letters:
            if popular_letters not in used_letters:
                return popular_letters, 0

    #print("getting most frequent letter: {}".format(chr(frequencies.index(max(frequencies)) + 97)))
    return chr(frequencies.index(max(frequencies)) + 97), max(frequencies)


def get_remaining_letters(letters_used):
    return list(set(most_popular_letters) - set(letters_used))


def main():

    rounds_played = 0
    while rounds_played < 100: #initialization step
        words_list, file = init()
        data = requests.get(endpoint).json()

        #temp = requests.post(endpoint + "/reset", data={'email': 'howardwang15@gmail.com'})

        #print(temp.status_code)
        state = data['state'].split()
        status = data['status']
        remaining_guesses = data['remaining_guesses']
        remaining_guesses_before_last_guess = remaining_guesses
        possible_words = get_words_same_length(state, words_list)

        assert (len(possible_words) == len(state)) #this should always be true
        for i in range(len(state)):
            for j in range(len(possible_words[i])):
                # print("state length: {0}, word length: {1}".format(len(state[i]), len(possible_words[i][j])))
                assert (len(possible_words[i][j]) == len(state[i]))


        used_letters = []
        char = 'e' #start guess with 'e'
        hack = False
        while status == 'ALIVE':
            if hack:
                break

            response = requests.post(endpoint, data={'guess': char})
            #print("char: {}".format(char))
            used_letters.append(char) #add most recently posted letter
            data = response.json()
            state = data['state'].split()
            status = data['status']
            remaining_guesses = data['remaining_guesses']

            #if remaining_guesses == remaining_guesses_before_last_guess:
            possible_words = find_possible_words(state, possible_words)

            if len(possible_words) != 0 and len(possible_words[0]) != 0 and possible_words[0][0] == 'Z':
                #print("error encountered")
                break

            remaining_guesses_before_last_guess = remaining_guesses
            only_word = False
            for words in possible_words:
                if len(words) == 1: #only one word left so be efficient
                    for letter in words[0]:
                        if letter not in used_letters:
                            char = letter
                            only_word = True

            if only_word:
                #print("only word")
                continue

            special_case = False
            for words in possible_words:
                for word in words:
                    if (len(word) == 1 or len(word) == 2) and 'a' not in used_letters: #hack for common 1-2 letter words
                        char = 'a'
                        special_case = True
                    elif (len(word) == 1 or len(word) == 2) and 'i' not in used_letters:
                        char = 'i'
                        special_case = True

            if not special_case:
                char, frequency = get_most_frequent_letter(possible_words, used_letters)

        rounds_played += 1
        #print("rounds_played: {}".format(rounds_played))

    #print(data['win_rate'])


if __name__ == '__main__':
    main()