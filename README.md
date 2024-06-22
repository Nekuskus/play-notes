# play-notes
A simple utility for playing music with the PC speaker. Makes use of a simple custom file format for encoding sound with notes.

## Usage
Invoke with:
```
python3 play-notes.py track.notes
```

## Sound format
Header contains global info for the playback:
- `BPM`
- `global_notelength` - defines how much of a beat each note will take up, can be overriden per note (example: 0.5)

Note formatting:
```
note [length] [delay]
```
Notes are expressed as `[A-G][#b]?\d` (ex: C#6, Bb5).

After every note, the rest of the remaining beat will be waited through with a delay, unless one is explicitly specified. This means that a note with the length 1.75 will have a delay of 0.25 by default.

Repeated sections are marked with directives:
- `start_section`
- `repeat_section N` - ends current section and appends it N times

Empty lines are skipped, comments are lines that start with `#`.

Formatted as follows:
```
BPM
global_notelength

# One note per line
A4

# Optionally, override length
# This one will take up two beats
A4 2

# Optionally, override both delay and length
# This note would normally play for half a beat and then be delayed for another half, instead the delay will be 1.5 times the beat length.
A4 0.5 1.5


# You can also repeat groups of notes!

start_section

A1
A2
A3

start_section

A4
A5

repeat_section 2

repeat_section 3

```
The extension `.notes` is preferred.

## Dependencies
This script relies on:
- an implementation of [`beep`](https://linux.die.net/man/1/beep) in your `$PATH`