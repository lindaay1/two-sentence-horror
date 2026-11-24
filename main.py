#!/usr/bin/env python3
"""Two-Sentence Horror — make.fun program entry.

Competition: u-suroto-two-sentence-horror-acea9253.

The tale below is the entrant's approved horror story, word for word,
in exactly two sentences: every night the phone in the empty room rang
once, and every night it was left to ring — until the night it was
answered, and the voice on the line was the teller's own, warning not
to answer because it is still in the house. The program's only job is
to carry those exact sentences into the folder the harness hands it,
so the sealed gate can read them from entry.txt.

The gate wants UTF-8 text of 1 to 400 characters, not only whitespace,
and the contest wants exactly two sentences. This file checks the tale
against both rules first, writes it to entry.txt and to a mirror copy
(horror.txt), then reads both files back and refuses to finish quietly
if either one came back different.

Standard library only. No network, no randomness, no arguments.
"""

import hashlib
import os
import re
import sys

HORROR_TALE = "Every night the phone in the empty room rang once, and every night I let it ring. Last night I picked up, and my own voice said: 'Don't answer \u2014 I'm still in the house.'"

LOW = 1
HIGH = 400
SENTENCES = 2
MAIN_FILE = "entry.txt"
MIRROR_FILE = "horror.txt"


def count_sentences(text):
    """Count sentences: a terminator [.?!] ending the text or followed by space."""
    stripped = text.strip()
    if stripped.endswith(("'", '"')):
        stripped = stripped[:-1]
    return len(re.findall(r"[.!?](?:\s|$)", stripped))


class HorrorTale:
    """One sealed two-sentence horror tale and the gate it must pass."""

    def __init__(self, tale, low=LOW, high=HIGH, sentences=SENTENCES):
        self.tale = tale
        self.low = low
        self.high = high
        self.sentences = sentences

    def encode(self):
        """Encode the tale after proving it fits the gate."""
        if not isinstance(self.tale, str):
            raise TypeError("horror tale must be text")
        count = len(self.tale)
        if count < self.low or count > self.high:
            raise ValueError(
                "horror tale is %d chars, gate is %d-%d" % (count, self.low, self.high)
            )
        if self.tale.strip() == "":
            raise ValueError("horror tale must not be only whitespace")
        if "\n" in self.tale or "\r" in self.tale:
            raise ValueError("horror tale must be one paragraph")
        found = count_sentences(self.tale)
        if found != self.sentences:
            raise ValueError("horror tale has %d sentences, need %d" % (found, self.sentences))
        return self.tale.encode("utf-8")

    def dispatch(self, outdir):
        """Write the tale to both files and prove they match."""
        data = self.encode()
        want = hashlib.sha256(data).hexdigest()
        os.makedirs(outdir, exist_ok=True)
        for name in (MAIN_FILE, MIRROR_FILE):
            path = os.path.join(outdir, name)
            with open(path, "wb") as handle:
                handle.write(data)
            with open(path, "rb") as handle:
                got = hashlib.sha256(handle.read()).hexdigest()
            if got != want:
                raise AssertionError(name + " came back different")
        return want


def main():
    tale = HorrorTale(HORROR_TALE)
    if "--check" in sys.argv[1:]:
        data = tale.encode()
        print("gate ok: %d chars, %d sentences, sha256 %s"
              % (len(data.decode("utf-8")), count_sentences(tale.tale), hashlib.sha256(data).hexdigest()))
        return
    if "--proof" in sys.argv[1:]:
        parts = re.split(r"(?<=[.!?])\s+", tale.tale.strip().rstrip("'"))
        for i, sentence in enumerate(parts, 1):
            print("sentence %d: %s" % (i, sentence))
        return
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    print("entry sealed: " + tale.dispatch(outdir))


if __name__ == "__main__":
    main()
