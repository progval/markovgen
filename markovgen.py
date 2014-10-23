#!/usr/bin/env python3
import re
import sys
import random

REGEXPS = {
    'weechat': '^.*\t.+\t(<[^ ]+> )?(?P<message>.*)$',
    'xchat': '[a-z.]+ [0-9]+ [0-9:]+ <[^ ]+> (<[^ ]+> )?(?P<message>.*)$',
    'supybot': '^[^ ]*  (<[^ ]+> )?(?P<message>.*)$',
}

class Markov(object):

    def __init__(self, messages=None):
        self.cache = {}
        self.words = ['\n']
        if messages:
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

    def feed_from_file(self, fd, extracter):
        messages = [extracter.match(x) for x in fd.readlines()]
        messages = [x.group('message') for x in messages if x]
        for message in messages:
            self.feed(message)

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




def main():
    if len(sys.argv) < 3:
        print('Syntax: %s <extracter> <log file>' % sys.argv[0])
        exit(1)
    if sys.argv[1] not in REGEXPS:
        print('Supported extracters: %s' % ', '.join(REGEXPS))
        exit(1)
    regexp = REGEXPS[sys.argv[1]]
    extracter = re.compile(regexp)
    m = Markov()
    for filename in sys.argv[2:]:
        with open(filename) as fd:
            m.feed_from_file(fd, extracter)

    for x in range(0, 500):
        print(m.generate_markov_text())

if __name__ == '__main__':
    main()
