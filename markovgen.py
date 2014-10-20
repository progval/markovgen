import re
import sys
import random

class Markov(object):

    def __init__(self, messages):
        self.cache = {}
        self.words = ['\n']
        for message in messages:
            self.feed(message)


    def triples(self, words):
        """ Generates triples from the given data string. So if our string were
                "What a lovely day", we'd generate (What, a, lovely) and then
                (a, lovely, day).
        """

        if len(words) < 3:
            return

        for i in range(len(words) - 2):
            yield (words[i], words[i+1], words[i+2])

    def feed(self, message):
        splitted = message.split(' ')
        for w1, w2, w3 in self.triples(self.words[-1:] + splitted + ['\n']):
            key = (w1, w2)
            if key in self.cache:
                self.cache[key].append(w3)
            else:
                self.cache[key] = [w3]
        self.words.extend(splitted + ['\n'])

    def generate_markov_text(self, max_size=30):
        seed_word = '\n'
        while seed_word == '\n' or next_word == '\n':
            seed = random.randint(0, len(self.words)-3)
            seed_word, next_word = self.words[seed], self.words[seed+1]
        if random.choice([True, False, False]) and ('\n', seed_word) in self.cache:
            w1, w2 = '\n', seed_word
        else:
            w1, w2 = seed_word, next_word
        gen_words = []
        for i in range(max_size):
            gen_words.append(w1)
            new = '\n'
            new = random.choice(self.cache[(w1, w2)])
            if new == '\n':
                break
            w1, w2 = w2, new
        if w2 != '\n':
            gen_words.append(w2)
        return ' '.join(filter(lambda x:x!='\n', gen_words))


extracter = re.compile('^.*\t.+\t(<[^ ]+> )?(?P<message>.*)$')
messages = [extracter.match(x) for x in open(sys.argv[1]).readlines()]
messages = [x.group('message') for x in messages if x]

m = Markov(messages)
for x in range(0, 500):
    print(m.generate_markov_text())
