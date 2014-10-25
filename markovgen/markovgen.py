#!/usr/bin/env python3
import re
import sys
import codecs
import random

try:
    import chardet
except ImportError:
    try:
        import charade as chardet
    except ImportError:
        chardet = None

class Markov(object):

    def __init__(self, messages=None):
        self.forward_cache = {}
        self.backward_cache = {}
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

    def _add_key_to_cache(self, key, cache, w):
        if key in cache:
            cache[key].append(w)
        else:
            cache[key] = [w]

    def feed(self, message):
        splitted = message.split(' ')
        for w1, w2, w3 in self.triples(self.words[-1:] + splitted + ['\n']):
            self._add_key_to_cache((w1, w2), self.forward_cache, w3)
            self._add_key_to_cache((w3, w2), self.backward_cache, w1)
        self.words.extend(splitted + ['\n'])

    def feed_from_file(self, fd, extracter):
        list(map(self.feed, filter(bool, map(extracter, fd.readlines()))))

    def select_seed(self, seed_word, backward):
        d = -1 if backward else +1
        if not seed_word:
            # Select a random seed and a random next word
            seed_word = '\n'
            while seed_word == '\n' or next_word == '\n':
                seed = random.randint(1, len(self.words)-3)
                seed_word, next_word = self.words[seed], self.words[seed+d]
        elif seed_word in self.words:
            # List the indexes of the occurences of the seed in the words,
            # select one of them, and take the next word.
            possible_indexes = [i+1 for (i, x) in enumerate(self.words[1:-1])
                              if self.words[i+1] == seed_word]
            next_word = self.words[random.choice(possible_indexes)+d]
            if backward:
                assert (seed_word, next_word) in self.backward_cache
            else:
                assert (seed_word, next_word) in self.forward_cache
        else:
            raise ValueError('%s is not in the corpus.' % seed_word)
        return (seed_word, next_word)

    def generate_markov_text(self, max_size=30, seed_word=None, backward=False):
        (seed_word, next_word) = self.select_seed(seed_word, backward)
        cache = self.backward_cache if backward else self.forward_cache

        if random.choice([True, False, False]) and ('\n', seed_word) in cache:
            w1, w2 = '\n', seed_word
        else:
            w1, w2 = seed_word, next_word
        gen_words = []
        for i in range(max_size):
            gen_words.append(w1)
            new = '\n'
            new = random.choice(cache[(w1, w2)])
            if new == '\n':
                break
            w1, w2 = w2, new
        if w2 != '\n':
            gen_words.append(w2)
        if backward:
            gen_words = reversed(gen_words)
        return ' '.join(filter(lambda x:x!='\n', gen_words))



REGEXPS = {
    'weechat': '^.*\t.+\t(<[^ ]+> )?(?P<message>.*)$',
    'xchat': '[a-z.]+ [0-9]+ [0-9:]+ <[^ ]+> (<[^ ]+> )?(?P<message>.*)$',
    'supybot': '^[^ ]*  (<[^ ]+> )?(?P<message>.*)$',
}


def main():
    if len(sys.argv) < 3:
        print('Syntax: %s <extracter> <log file>' % sys.argv[0])
        exit(1)
    if sys.argv[1] not in REGEXPS:
        print('Supported extracters: %s' % ', '.join(REGEXPS))
        exit(1)
    regexp = re.compile(REGEXPS[sys.argv[1]])
    def extracter(x):
        encoding = 'utf8'
        if chardet:
            encoding = chardet.detect(x)['encoding']
        x = x.decode(encoding)
        msg = regexp.match(x)
        print(repr(msg.group('message')))
        if msg:
            return msg.group('message')
    m = Markov()
    for filename in sys.argv[2:]:
        with codecs.open(filename, 'rb') as fd:
            m.feed_from_file(fd, extracter)

    for x in range(0, 500):
        print(m.generate_markov_text())

if __name__ == '__main__':
    main()
