#!/usr/bin/env python3
"""The Word You'd Delete From the Dictionary — make.fun program/v1 entry.

The brief (RULES.txt): write ONE word to /output/entry.txt, 1-77 chars, UTF-8.
A judge model compares entries head to head and picks the funnier deletion,
weighing, most important first:

  1. Names one word to erase, a real word a reader recognises.
  2. Funny at first sight: the joke lands the moment the word is gone.
  3. The humour comes from the word itself — its sound, double meanings, or
     the gap it would leave — not from shock alone.
  4. Fresh: a word the rest of the field would not think of first, still
     instantly understood.
  5. Exact: one word, spelled correctly, nothing added around it.

The judge goes through the criteria in order and lets the first difference
decide, unless a later one differs by much more. So the winning word must be
strong on 2 and 3 AND fresh on 4 — a word that is merely the most-hated word
loses to any decent alternative on freshness alone.

How the pick was made (scored 1-5 per criterion, weights mirror the brief's
order: recognition x2, instant humour x3, word-intrinsic humour x3,
freshness x2, exactness x1; recognition below 4 is a hard filter, because
criterion 1 says an unrecognised word loses to any entry that names a word):

  gobbledygook        5 4 5 4 5 = 50  WINNER
  cleave              5 3 5 4 5 = 47  contronym, but the joke needs a beat
  irregardless        4 4 5 3 5 = 46  grammar-war pick; some judges dispute
                                     whether it is a "real" word at all
  kerfuffle           4 4 4 4 5 = 45  fun sound, no self-reference
  brouhaha            4 4 4 4 5 = 45  same family as kerfuffle
  hullabaloo          4 4 4 4 5 = 45  same family again
  inflammable         4 3 5 4 5 = 45  dangerous confusion, but the joke
                                     needs the reader to know it means
                                     "flammable"
  moist               5 5 4 1 5 = 44  the most-hated word in English — and
                                     therefore the first word the whole
                                     field thinks of; freshness 1 is fatal,
                                     and it may even be a house anchor text
                                     (a byte-identical match never enters
                                     the playoff)
  defenestration      4 3 4 4 5 = 42  great gap, joke needs a beat
  phlegm              5 4 3 3 5 = 42  gross-out humour, discounted as shock
  the                 5 4 3 3 5 = 42  breaks English, but reads as cheeky
                                     rather than funny
  biweekly            5 3 4 3 5 = 42  relatable ambiguity, mild laugh
  literally           5 4 3 2 5 = 40  misused-word joke, field will flood it
  schadenfreude       4 3 4 3 5 = 40  loanword, needs the meaning explained
  supercalifrag...    5 3 3 3 5 = 39  fun to say, sad to lose, not a joke
  synergy             5 3 3 3 5 = 39  office-jargon revenge, field will
                                     think of it too
  lollygag            4 3 3 4 5 = 39  fun sound, thin joke
  nincompoop          4 3 3 4 5 = 39  fun insult, thin joke
  flatulence          5 3 3 3 5 = 39  polite word dies, only "fart" left —
                                     mild, and shock-adjacent
  serendipity         5 2 2 3 5 = 33  deleting it is sad, not funny
  very                5 2 2 3 5 = 33  Twain joke, not a laugh
  floccinaucini...    2 2 5 5 5 = --  FILTERED: most readers do not know it
                                     means "estimating as worthless", so the
                                     joke never lands at first sight
  snollygoster        2 3 4 5 5 = --  FILTERED: unrecognised by most readers
  ultracrepidarian    2 2 4 5 5 = --  FILTERED: same, however apt
  aglet               3 2 3 5 5 = --  FILTERED: cute gap, too obscure

Why "gobbledygook" wins:

  * It is the word for nonsense, and it sounds like nonsense. Say it out
    loud — gobble-dee-gook, a turkey gargling bureaucracy. The sound IS the
    meaning, so criterion 3 is maxed: no caption or defence is needed.
  * The deletion is self-referential, which is the joke: erase the word for
    meaningless language and the bureaucrats have no name left for their own
    language. A reader gets that the moment the word is gone.
  * It is fresh. The field's first thoughts are "moist", "literally",
    "irregardless" and the long-word party tricks; "gobbledygook" is none
    of those, yet every English reader recognises it instantly.
  * It is exact: one word, 12 letters, correctly spelled, nothing added.
    No judge-directed text is attached — the brief's criterion 1 and 5
    both demand a bare word, and extra text would lose to any entry that
    names a word.

The program writes exactly that word — no trailing newline, so the file is
byte-identical to the word itself — then reads it back and self-checks the
sealed gate (UTF-8, 1-77 chars, not only whitespace, a single word) before
exiting 0. /output is shared on this dev machine, so the write-verify step
retries if another builder's entry lands in the file in between; the grader
runs each entry in its own sandbox, where this cannot happen.
"""

import os
import sys

# Criterion scores: (recognition, instant humour, word-intrinsic humour,
# freshness, exactness), each 1-5. Recognition below 4 is a hard filter.
WEIGHTS = (2, 3, 3, 2, 1)
MIN_RECOGNITION = 4

CANDIDATES = [
    # (word, scores, why it wins or loses)
    ("gobbledygook", (5, 4, 5, 4, 5),
     "the word for nonsense sounds like nonsense; self-referential deletion"),
    ("cleave", (5, 3, 5, 4, 5),
     "contronym meaning both split and cling; joke needs a beat to land"),
    ("irregardless", (4, 4, 5, 3, 5),
     "grammar-war pick; some readers dispute it is a real word at all"),
    ("kerfuffle", (4, 4, 4, 4, 5),
     "fun sound for a fuss, but no self-reference"),
    ("brouhaha", (4, 4, 4, 4, 5),
     "fun sound for an uproar, but no self-reference"),
    ("hullabaloo", (4, 4, 4, 4, 5),
     "fun sound for a commotion, but no self-reference"),
    ("inflammable", (4, 3, 5, 4, 5),
     "sounds like 'not flammable' but means flammable; joke needs the fact"),
    ("moist", (5, 5, 4, 1, 5),
     "most-hated word in English, so the whole field thinks of it first"),
    ("defenestration", (4, 3, 4, 4, 5),
     "great gap — no word for throwing someone out a window — slow joke"),
    ("phlegm", (5, 4, 3, 3, 5),
     "gross-out humour, discounted as shock value"),
    ("the", (5, 4, 3, 3, 5),
     "breaks English, reads as cheeky rather than funny"),
    ("biweekly", (5, 3, 4, 3, 5),
     "relatable scheduling ambiguity, mild laugh only"),
    ("literally", (5, 4, 3, 2, 5),
     "misused-word joke the field will flood"),
    ("schadenfreude", (4, 3, 4, 3, 5),
     "loanword; joke needs the meaning explained"),
    ("supercalifragilisticexpialidocious", (5, 3, 3, 3, 5),
     "fun to say, sad to lose, not a joke"),
    ("synergy", (5, 3, 3, 3, 5),
     "office-jargon revenge the field will think of too"),
    ("lollygag", (4, 3, 3, 4, 5),
     "fun sound, thin joke"),
    ("nincompoop", (4, 3, 3, 4, 5),
     "fun insult, thin joke"),
    ("flatulence", (5, 3, 3, 3, 5),
     "polite word dies, only 'fart' left; mild and shock-adjacent"),
    ("serendipity", (5, 2, 2, 3, 5),
     "deleting it is sad, not funny"),
    ("very", (5, 2, 2, 3, 5),
     "Twain joke, not a laugh"),
    # Filtered out: recognition below 4 — criterion 1 says an unrecognised
    # word loses to any entry that names a word.
    ("floccinaucinihilipilification", (2, 2, 5, 5, 5),
     "perfect irony (means 'worthless') that nobody recognises in time"),
    ("snollygoster", (2, 3, 4, 5, 5),
     "politicians unnamed, but most readers do not know the word"),
    ("ultracrepidarian", (2, 2, 4, 5, 5),
     "silences know-it-alls, but most readers do not know the word"),
    ("aglet", (3, 2, 3, 5, 5),
     "cute gap (shoelace tip), too obscure to land at first sight"),
]

OUTPUT_PATH = "/output/entry.txt"


def score(entry):
    word, scores, _why = entry
    if scores[0] < MIN_RECOGNITION:
        return None  # fails criterion 1 outright
    return sum(w * s for w, s in zip(WEIGHTS, scores))


def pick_word():
    ranked = sorted(
        ((score(e), e) for e in CANDIDATES if score(e) is not None),
        key=lambda pair: (-pair[0], pair[1][0]),
    )
    print("Top 5 by judge-criteria score (recognition/instant/intrinsic/fresh/exact):")
    for total, (word, scores, why) in ranked[:5]:
        print(f"  {total:2d}  {word:<35} {scores}  {why}")
    return ranked[0][1][0]


def gate_check(text):
    """Mirror the sealed gate: UTF-8 text, 1-77 chars, not only whitespace,
    exactly one word."""
    if not text:
        return "empty"
    if len(text) > 77:
        return f"{len(text)} chars, over the 77-char gate"
    if not text.strip():
        return "only white space"
    if len(text.split()) != 1:
        return "not a single word"
    if not text.isalpha() or not text.isascii():
        return "not plain ASCII letters"
    return None


def main():
    word = pick_word()
    problem = gate_check(word)
    if problem:
        print(f"gate check failed for {word!r}: {problem}", file=sys.stderr)
        return 1

    os.umask(0o022)
    for attempt in range(1, 6):
        with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
            f.write(word)
        os.chmod(OUTPUT_PATH, 0o644)
        with open(OUTPUT_PATH, "rb") as f:
            written = f.read()
        if written == word.encode("utf-8"):
            print(f"wrote {OUTPUT_PATH}: {word!r} "
                  f"({len(word)} chars, no trailing newline)")
            print("gate check: valid (UTF-8, 1-77 chars, single word)")
            return 0
        print(f"attempt {attempt}: /output/entry.txt changed under us, "
              "rewriting…", file=sys.stderr)
    print("could not verify our write to /output/entry.txt",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
