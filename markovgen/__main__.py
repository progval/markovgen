import re
import sys
from .markovgen import Markov

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
        msg = regexp.match(x)
        if msg:
            return msg.group('message')
    m = Markov()
    for filename in sys.argv[2:]:
        with open(filename) as fd:
            m.feed_from_file(fd, extracter)

    for x in range(0, 500):
        print(m.generate_markov_text())

if __name__ == '__main__':
    main()

