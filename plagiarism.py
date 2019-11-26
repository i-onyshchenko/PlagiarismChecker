import itertools

from text_matcher.matcher import Matcher, Text
from text_matcher.text_matcher import getFiles, checkLog, createLog


class PlagiarismChecker:
    def __init__(self):
        pass

    def __count_words(self, file, poses):
        """

        :param poses: list of intervals of plagiarism
        :return: num of plagiarised words
        """
        res = 0
        for pos in poses:
            res += file[pos[0]:pos[1]].count(' ') + 1

        return res

    def check(self, text1, text2, threshold=10, cutoff=0.5, ngrams=1, logfile="log.txt", stops=False):
        """ This program finds similar text in two text files. """

        # Determine whether the given path is a file or directory.

        texts1 = getFiles(text1)
        texts2 = getFiles(text2)

        pairs = list(itertools.product(texts1, texts2))

        numPairs = len(pairs)

        texts = {}
        prevTextObjs = {}
        for filename in texts1 + texts2:
            with open(filename, errors="ignore") as f:
                text = f.read()
            if filename not in texts:
                texts[filename] = text

        for index, pair in enumerate(pairs):

            # Make sure we haven't already done this pair.
            inLog = checkLog(logfile, [pair[0], pair[1]])

            if inLog is None:
                # This means that there isn't a log file. Let's set one up.
                # Set up columns and their labels.
                columnLabels = ['Text A', 'Text B', 'Threshold', 'Cutoff', 'N-Grams', 'Num Matches', 'Text A Length',
                                'Text B Length', 'Locations in A', 'Locations in B']
                print('No log file found. Setting one up.')
                createLog(logfile, columnLabels)

            if inLog:
                print('This pair is already in the log. Skipping.')
                continue

            filenameA, filenameB = pair[0], pair[1]
            textA, textB = texts[filenameA], texts[filenameB]

            # Put this in a dictionary so we don't have to process a file twice.
            for filename in [filenameA, filenameB]:
                if filename not in prevTextObjs:
                    print('Processing text: %s' % filename)
                    prevTextObjs[filename] = Text(texts[filename], filename, removeStopwords=stops)

            # Just more convenient naming.
            textObjA = prevTextObjs[filenameA]
            textObjB = prevTextObjs[filenameB]

            # Reset the table of previous text objects, so we don't overload memory.
            # This means we'll only remember the previous two texts.
            prevTextObjs = {filenameA: textObjA, filenameB: textObjB}

            # Do the matching.
            myMatch = Matcher(textObjA, textObjB, threshold=threshold, cutoff=cutoff, ngramSize=ngrams,
                              removeStopwords=stops)
            num_matches, locA, locB = myMatch.match()
            percent = self.__count_words(textObjA.text, locA)/(textObjA.text.count(' ') + 1)
            print("Percents of {} in file {} : {}".format(filenameB, filenameA, percent))


def main():
    # ta = Text(open('text_test.txt').read(), 'text1', removeStopwords=False)
    # tb = Text(open('text2.txt').read(), 'text2', removeStopwords=False)
    #
    # Matcher(ta, tb, threshold=10, ngramSize=1).match()
    checker = PlagiarismChecker()
    checker.check("text_test.txt", "texts/", threshold=10, ngrams=1, cutoff=0.4, stops=False)


if __name__ == "__main__":
    main()

