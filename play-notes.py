import subprocess
import sys
import math


filename = ''
debug = False
dry = False
for arg in sys.argv[1:]:
    if arg == '-v' or arg == '--verbose':
        debug = True
    elif arg == '-d' or arg == '--dry-run':
        debug = True
        dry = True
    else:
        filename = arg

# Table from: https://mixbutton.com/mixing-articles/music-note-to-frequency-chart/
"""
C
    16.35 Hz     32.70 Hz     65.41 Hz     130.81 Hz     261.63 Hz     523.25 Hz     1046.50 Hz     2093.00 Hz     4186.01 Hz
C#/Db
    17.32 Hz     34.65 Hz     69.30 Hz     138.59 Hz     277.18 Hz     554.37 Hz     1108.73 Hz     2217.46 Hz     4434.92 Hz
D
    18.35 Hz     36.71 Hz     73.42 Hz     146.83 Hz     293.66 Hz     587.33 Hz     1174.66 Hz     2349.32 Hz     4698.63 Hz
D#/Eb
    19.45 Hz     38.89 Hz     77.78 Hz     155.56 Hz     311.13 Hz     622.25 Hz     1244.51 Hz     2489.02 Hz     4978.03 Hz
E
    20.60 Hz     41.20 Hz     82.41 Hz     164.81 Hz     329.63 Hz     659.25 Hz     1318.51 Hz     2637.02 Hz     5274.04 Hz
F
    21.83 Hz     43.65 Hz     87.31 Hz     174.61 Hz     349.23 Hz     698.46 Hz     1396.91 Hz     2793.83 Hz     5587.65 Hz
F#/Gb
    23.12 Hz     46.25 Hz     92.50 Hz     185 Hz        369.99 Hz     739.99 Hz     1479.98 Hz     2959.96 Hz     5919.91 Hz
G
    24.50 Hz     49 Hz        98 Hz        196 Hz        392 Hz        783.99 Hz     1567.98 Hz     3135.96 Hz     6271.93 Hz
G#/Ab
    25.96 Hz     51.91 Hz     103.83 Hz    207.65 Hz     415.30 Hz     830.61 Hz     1661.22 Hz     3322.44 Hz     6644.88 Hz
A
    27.50 Hz     55 Hz        110 Hz       220 Hz        440 Hz        880 Hz        1760 Hz        3520 Hz        7040 Hz
A#/Bb
    29.14 Hz     58.27 Hz     116.54 Hz    233.08 Hz     466.16 Hz     932.33 Hz     1864.66 Hz     3729.31 Hz     7458.62 Hz
B
    30.87 Hz     61.74 Hz     123.47 Hz    246.94 Hz     493.88 Hz     932.33 Hz     1975.53 Hz     3951.07 Hz     7902.13 Hz
"""

halftones_log = []

def getNoteOrd(letter: str):
    match letter:
        case "C":
            return 0
        case "D":
            return 2
        case "E":
            return 4
        case "F":
            return 5
        case "G":
            return 7
        case "A":
            return 9
        case "B":
            return 11

def getFreq(note: str, octave: int) -> float:
    A4 = 440

    letter = note[0].upper()
    n = getNoteOrd(letter)

    if len(note) > 1:
        if note[1] == '#':
            n += 1
        elif note[1] == 'b':
            n -= 1

    n += octave * 12
    
    halftones_log.append(n) # Log diff from C0, to avoid negatives

    n -= 4 * 12 + 9 # - 57, offset by A4

    
    return A4 * 2 ** (n / 12)


bar = 1

notesfile = open(filename)

beatms = math.trunc((60 / float(notesfile.readline())) * 1000)
global_beatlength = float(notesfile.readline())

lines = notesfile.read().splitlines()

notes = []

sections = []

for line in lines:
    line = line.strip()

    if len(line) == 0 or line.startswith('#'):
        continue
    if line == "start_section":
        sections.append([])
        continue

    if line.startswith("repeat_section"):
        section = sections.pop()
        if len(sections) > 0:
            sections[-1].extend(section * int(line.split(' ')[1]))
        else:
            notes.extend(section * int(line.split(' ')[1]))
        continue

    split = line.split(' ')
    note = [split[0]]

    if len(split) > 1:
        note.append(float(split[1]))

    if len(split) > 2:
        note.append(float(split[2]))

    if len(sections) > 0:
        sections[-1].append(note)
    else:
        notes.append(note)

notesfile.close()

constructed = ["beep"]

for entry in notes:
    note_beatlength = global_beatlength
    if(len(entry) > 1):
        note_beatlength = entry[1]
    
    length = note_beatlength * beatms
    
    delay = (bar - (note_beatlength % 1 if note_beatlength % 1 != 0 else 1)) * beatms
    if(len(entry) > 2):
        delay = entry[2] * beatms
    
    note = entry[0][:-1]
    octave = int(entry[0][-1])

    frequency = getFreq(note, octave)
    
    # Frequency is rounded to save argument character count, and will be rounded for kernel API anyways as per `man beep`
    constructed.extend(['-f', f"{round(frequency)}", '-D', f"{delay}", '-l', f"{length}", '-n'])

constructed = constructed[:-1] # remove trailing '-n'

if debug:
    print(halftones_log)
    print(constructed)

if not dry:
    subprocess.run(constructed)