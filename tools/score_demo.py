"""Write the demo film's score - an original piece, synthesised here.

    python tools/score_demo.py "%TEMP%\\wq-demo\\shoot\\score.wav"

Nothing is sampled and nothing is licensed: every sound is built from sine
partials, so the file this writes is ours to publish. It is deliberately a bed
rather than a tune - sparse bell notes over a warm pad, quiet enough that a
viewer reads the captions instead of listening to it.

The shape follows the film: a single swell under the title, sparse and low
while the manager types, a lift when the task reaches the strip, warmest over
the reporting, and a resolve under the end card. compose_demo.py calls this and
muxes the result, so there is usually no need to run it by hand.
"""
import math
import os
import struct
import sys
import wave

import numpy as np

SR = 44100
LENGTH = 67.0                      # the film's running time


def note(freq, dur, amp=1.0, decay=2.6, partials=(1.0, 0.42, 0.19, 0.08)):
    """A struck note: a few partials under one exponential decay."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.exp(-t * decay)
    # A short attack keeps the transient from clicking.
    env *= np.minimum(1.0, t / 0.006)
    out = np.zeros(n)
    for i, level in enumerate(partials):
        # Partials of a struck string sit slightly sharp of the harmonic.
        out += level * np.sin(2 * math.pi * freq * (i + 1) * (1 + 0.0006 * i) * t)
    return out * env * amp / sum(partials)


def pad(freqs, dur, amp=1.0, attack=1.4, release=1.8):
    """A sustained chord, slightly detuned against itself so it breathes."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for detune in (-0.13, 0.0, 0.15):
            drift = 1 + 0.0009 * np.sin(2 * math.pi * (0.06 + 0.013 * f % 0.05) * t)
            out += np.sin(2 * math.pi * (f + detune) * drift * t)
    out /= len(freqs) * 3

    env = np.ones(n)
    a = min(int(attack * SR), n // 2)
    r = min(int(release * SR), n // 2)
    env[:a] = np.linspace(0, 1, a) ** 1.6
    env[n - r:] = np.linspace(1, 0, r) ** 1.4
    return out * env * amp


def bass(freq, dur, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / 0.35) * np.minimum(1.0, (dur - t) / 0.6)
    return (np.sin(2 * math.pi * freq * t)
            + 0.16 * np.sin(2 * math.pi * freq * 2 * t)) * env * amp * 0.6


def lowpass(x, cutoff):
    """One-pole low pass - enough to take the glare off the pad."""
    a = math.exp(-2 * math.pi * cutoff / SR)
    out = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        out[i] = acc
    return out


def reverb(x, mix=0.34):
    """A handful of decaying taps. Not a hall, but it stops it sounding dry."""
    out = x.copy()
    for delay, level in ((0.031, 0.5), (0.053, 0.38), (0.079, 0.3),
                         (0.117, 0.24), (0.181, 0.17), (0.263, 0.11)):
        d = int(delay * SR)
        tail = np.zeros_like(x)
        tail[d:] = x[:-d] * level
        out += tail * mix
    return out


def place(track, signal, at, gain=1.0):
    start = int(at * SR)
    end = min(len(track), start + len(signal))
    if start >= len(track) or end <= start:
        return
    track[start:end] += signal[:end - start] * gain


# --- the piece -------------------------------------------------------------
# C major, 68 bpm. Four chords, seven seconds each, twice and a bit - slow
# enough that nothing lands on a cut by accident.

def hz(semitones_from_a4):
    return 440.0 * (2 ** (semitones_from_a4 / 12))

N = {"C2": hz(-33), "G2": hz(-26), "A2": hz(-24), "F2": hz(-28),
     "C3": hz(-21), "E3": hz(-17), "G3": hz(-14), "A3": hz(-12), "F3": hz(-16),
     "C4": hz(-9), "D4": hz(-7), "E4": hz(-5), "G4": hz(-2), "A4": hz(0),
     "C5": hz(3), "D5": hz(5), "E5": hz(7), "G5": hz(10), "A5": hz(12), "C6": hz(15)}

CHORDS = [
    ("C",  N["C2"], [N["C3"], N["E3"], N["G3"]], [N["C5"], N["E5"], N["G5"], N["E5"]]),
    ("G",  N["G2"], [N["G3"], N["C4"], N["E4"]], [N["D5"], N["G5"], N["E5"], N["D5"]]),
    ("Am", N["A2"], [N["A3"], N["C4"], N["E4"]], [N["E5"], N["A5"], N["C6"], N["A5"]]),
    ("F",  N["F2"], [N["F3"], N["A3"], N["C4"]], [N["C5"], N["F3"] * 4, N["A5"], N["G5"]]),
]
BAR = 7.0            # seconds per chord


def build():
    n = int(LENGTH * SR)
    bells = np.zeros(n)
    pads = np.zeros(n)
    lows = np.zeros(n)

    # The title card gets one swell of its own before the loop starts.
    place(pads, pad([N["C3"], N["E3"], N["G3"]], 5.4, 0.9, attack=1.6, release=2.2), 0.0)
    place(bells, note(N["C5"], 4.0, 0.5, decay=1.5), 0.6)

    at = 3.2
    step = 0
    while at < LENGTH:
        name, root, chord, arp = CHORDS[step % len(CHORDS)]
        place(pads, pad(chord, BAR + 1.4, 0.75), at)
        place(lows, bass(root, BAR + 0.8, 0.8), at)

        # Four bell notes to the chord, the last one held back a little.
        for i, f in enumerate(arp):
            when = at + i * (BAR / 4) + (0.18 if i == 3 else 0.0)
            if when >= LENGTH:
                break
            amp = (0.5, 0.34, 0.44, 0.3)[i]
            place(bells, note(f, 5.0, amp, decay=1.25), when)
            if i == 2:                      # a quiet octave shadow
                place(bells, note(f * 2, 3.0, amp * 0.16, decay=2.0), when + 0.09)
        at += BAR
        step += 1

    # How loud the piece is, section by section: under the title, through the
    # typing, the lift when it reaches her screen, and the resolve at the end.
    curve = [(0.0, 0.55), (3.2, 0.42), (17.0, 0.5), (23.4, 0.74),
             (32.4, 0.8), (43.2, 0.88), (48.6, 1.0), (58.0, 0.94),
             (62.0, 0.8), (67.0, 0.0)]
    t = np.arange(n) / SR
    gain = np.interp(t, [p[0] for p in curve], [p[1] for p in curve])

    pads = lowpass(pads, 1500)
    lows = lowpass(lows, 220)

    dry = bells * 0.5 + pads * 0.30 + lows * 0.24
    wet = reverb(dry, mix=0.32) * gain

    # Open and close with the picture.
    fade_in = np.minimum(1.0, t / 1.2)
    fade_out = np.minimum(1.0, np.maximum(0.0, (LENGTH - t) / 2.6))
    wet *= fade_in * fade_out

    # A gentle stereo spread: the same piece, a few milliseconds apart.
    off = int(0.011 * SR)
    left = wet.copy()
    right = np.zeros_like(wet)
    right[off:] = wet[:-off]
    right = right * 0.86 + wet * 0.14

    stereo = np.stack([left, right], axis=1)
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo *= 0.62 / peak            # a bed, not a soundtrack album
    return stereo


def write(path, stereo):
    data = np.clip(stereo, -1.0, 1.0)
    pcm = (data * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    dest = os.path.abspath(sys.argv[1])
    audio = build()
    write(dest, audio)
    rms = float(np.sqrt(np.mean(audio ** 2)))
    print("wrote %s  %.1fs  peak %.2f  rms %.3f (%.1f dBFS)"
          % (dest, len(audio) / SR, float(np.max(np.abs(audio))), rms,
             20 * math.log10(rms) if rms else -99))
