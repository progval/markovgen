#!/usr/bin/env python3
import re
import sys
import codecs
import random
import sqlite3
import tempfile
import logging

__all__ = ['Markov', 'mixed_encoding_extracting', 'REGEXPS']

logger = logging.Logger('markovgen')

try:
    import chardet
except ImportError:
    try:
        import charade as chardet
    except ImportError:
        chardet = None

if sys.version_info[0] >= 3:
    intern = sys.intern

class Markov(object):

    def __init__(self, messages=None):
        self._create_db()
        self.last_words = []
        if messages:
            for message in messages:
                self.feed(message)

    def _create_db(self):
        #self._tempfile = tempfile.NamedTemporaryFile()
        #self.db = c = sqlite3.connect(self._tempfile.name)
        self.db = c = sqlite3.connect(':memory:')
        with c:
            #c.execute('CREATE TABLE triples (w1, w2, w3, nb, CONSTRAINT uniqueness UNIQUE(w1, w2, w3));')
            c.execute('CREATE TABLE triples (w1, w2, w3);')
            #c.execute('CREATE INDEX forward ON triples (w1, w2)')
            #c.execute('CREATE INDEX backward ON triples (w2, w3)')


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
        splitted = list(map(intern, message.split(' ')))
        with self.db:
            #for triple in self.triples(self.last_words[-2:] + splitted + ['\n']):
            #    self.db.execute('INSERT OR IGNORE INTO triples VALUES (?, ?, ?, 0);', triple)
            #    self.db.execute('UPDATE triples SET nb=nb+1 WHERE w1==? AND w2==? and w3==?;', triple)
            self.db.executemany('INSERT INTO triples VALUES (?, ?, ?);',
                    self.triples(self.last_words[-2:] + splitted + ['\n']))
        self.last_words = (self.last_words + splitted[0:2])[-2:]

    def feed_from_file(self, fd, extracter):
        list(map(self.feed, filter(bool, map(extracter, fd.readlines()))))

    def select_seed(self, seed_word, backward):
        d = -1 if backward else +1
        if not seed_word:
            # Select a random seed and a random next word
            c = self.db.cursor()
            c.execute('SELECT w1, w2 FROM triples WHERE w1 != "\\n" AND w2 != "\\n" ORDER BY random() LIMIT 1;')
            (seed_word, next_word) = c.fetchone()
        elif seed_word in self.words:
            # List the indexes of the occurences of the seed in the words,
            # select one of them, and take the next word.
            c = self.db.cursor()
            c.execute('SELECT w1, w2 FROM triples WHERE w1 == ? AND w2 != "\\n" ORDER BY random() LIMIT 1;', (seed_word,))
            (seed_word, next_word) = c.fetchone()
        else:
            raise ValueError('%s is not in the corpus.' % (seed_word,))
        return (seed_word, next_word)

    def generate_markov_text(self, max_size=30, seed=None, backward=False,
            seed_word=None):
        if seed_word:
            logger.warning('Use of deprecated argument `seed_word` to '
                           'markovgen.Markov.generate_markov_text().')
            seed = seed_word
        if isinstance(seed, (tuple, list)):
            (seed_word, next_word) = seed
        else:
            (seed_word, next_word) = self.select_seed(seed, backward)

        c = self.db.cursor()


        w1, w2 = seed_word, next_word
        if random.choice([True, False, False]):
            if backward:
                c.execute('SELECT w1 FROM triples WHERE w2 == ? AND w3 == "\\n" ORDER BY random() LIMIT 1', (seed_word,))
            else:
                c.execute('SELECT w3 FROM triples WHERE w1 == "\\n" AND w2 == ? ORDER BY random() LIMIT 1', (seed_word,))
            r = c.fetchone()
            if r is not None:
                w1, w2 = r

        (w1, w2) = intern(w1), intern(w2)
        gen_words = []
        for i in range(max_size):
            gen_words.append(w1)
            new = '\n'
            if backward:
                c.execute('SELECT w1 FROM triples WHERE w2 == ? AND w3 == ? ORDER BY random() LIMIT 1', (w1, w2))
            else:
                c.execute('SELECT w3 FROM triples WHERE w1 == ? AND w2 == ? ORDER BY random() LIMIT 1', (w1, w2))
            r = c.fetchone()
            if r is None:
                break
            else:
                (new,) = r
            if new == '\n':
                break
            w1, w2 = w2, new
        if w2 != '\n':
            gen_words.append(w2)
        if backward:
            gen_words = reversed(gen_words)
        return ' '.join(filter(lambda x:x!='\n', gen_words))

def mixed_encoding_extracting(f):
    def newf(msg):
        try:
            msg = msg.decode()
        except UnicodeDecodeError:
            if chardet:
                encoding = chardet.detect(msg)['encoding']
                try:
                    msg = msg.decode(encoding)
                except UnicodeDecodeError:
                    return None
        return f(msg)
    return newf

if sys.version_info[0] < 3:
    mixed_encoding_extracting = lambda f:f

REGEXPS = {
    'weechat': '^.*\t.+\t(<[^ ]+> )?(?P<message>.*)$',
    'xchat': '[a-z.]+ [0-9]+ [0-9:]+ <[^ ]+> (<[^ ]+> )?(?P<message>.*)$',
    'supybot': '^[^ ]*  (<[^ ]+> )?(?P<message>.*)$',
    'srt': '^(?P<message>[^0-9].*)$',
    'plain': '^(?P<message>.*)$'
}


def main():
    if len(sys.argv) < 3:
        print('Syntax: %s <extracter> <log file>' % sys.argv[0])
        exit(1)
    if sys.argv[1] not in REGEXPS:
        print('Supported extracters: %s' % ', '.join(REGEXPS))
        exit(1)
    regexp = re.compile(REGEXPS[sys.argv[1]])
    @mixed_encoding_extracting
    def extracter(x):
        msg = regexp.match(x)
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
