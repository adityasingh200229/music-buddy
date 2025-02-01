import random
from midiutil import MIDIFile

# MIDI drum note numbers (General MIDI drum map)
DRUM_NOTES = {
    'kick': 36,        # Bass Drum 1
    'snare': 38,       # Acoustic Snare
    'hihat_closed': 42,  # Closed Hi-Hat
    'hihat_open': 46,    # Open Hi-Hat
    'crash': 49,       # Crash Cymbal 1
    'ride': 51,        # Ride Cymbal 1
    'tom_high': 50,    # High Tom
    'tom_mid': 47,     # Mid Tom
    'tom_low': 43      # Low Tom
}

def get_scale(key='C', scale_type='major', octaves=2, base_octave=4):
    """Generate a musical scale based on key and type across multiple octaves."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    intervals = {
        'major': [2, 2, 1, 2, 2, 2, 1],
        'minor': [2, 1, 2, 2, 1, 2, 2]
    }

    start_idx = notes.index(key)
    scale_notes = []

    for octave in range(octaves):
        current_idx = start_idx
        octave_notes = []

        for interval in intervals[scale_type]:
            note = notes[current_idx]
            octave_notes.append((note, base_octave + octave))
            current_idx = (current_idx + interval) % 12

        scale_notes.extend(octave_notes)

    return scale_notes

def get_chord_progression(scale_type='major'):
    """Get varied chord progressions based on scale type."""
    if scale_type == 'major':
        progressions = [
            [1, 4, 5, 1],  # I-IV-V-I
            [1, 6, 4, 5],  # I-vi-IV-V
            [2, 5, 1, 6],  # ii-V-I-vi
            [1, 5, 6, 4]   # I-V-vi-IV
        ]
    else:
        progressions = [
            [1, 6, 4, 5],  # i-vi-iv-v
            [1, 4, 7, 5],  # i-iv-VII-v
            [6, 4, 1, 5],  # vi-iv-i-v
            [1, 7, 6, 5]   # i-VII-vi-v
        ]
    return random.choice(progressions)

def note_to_midi_number(note, octave):
    """Convert a note name and octave to MIDI note number."""
    notes = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 
             'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    return 60 + notes[note] + (octave - 4) * 12

def generate_drum_pattern(measures=8, time_signature=4):
    """Generate a more varied drum pattern with full drum kit."""
    pattern = []
    for measure in range(measures):
        base_time = measure * time_signature

        # Basic pattern variations with full drum kit
        patterns = [
            # Standard rock pattern
            [('kick', 0), ('hihat_closed', 0), ('snare', 1), ('hihat_closed', 1),
             ('kick', 2), ('hihat_closed', 2), ('snare', 3), ('hihat_closed', 3),
             ('crash', 0)],  # Crash on measure start

            # Syncopated pattern
            [('kick', 0), ('hihat_closed', 0.5), ('snare', 1), ('hihat_open', 1.5),
             ('kick', 2), ('hihat_closed', 2.5), ('snare', 3), ('ride', 3.5),
             ('tom_high', 3.75)],

            # Fill pattern
            [('kick', 0), ('snare', 1), ('tom_high', 2), ('tom_mid', 2.25),
             ('tom_low', 2.5), ('snare', 3), ('crash', 3.75)]
        ]

        # Choose a random pattern for this measure
        current_pattern = random.choice(patterns)

        # Add the pattern with the correct timing offset
        for drum, beat in current_pattern:
            pattern.append((drum, base_time + beat))

    return pattern

def generate_midi(filename, tempo=120, key='C', scale_type='major', base_octave=4, length=32, 
                 enable_chords=True, enable_drums=True):
    """Generate a MIDI file with melody, chords, and drums."""
    midi = MIDIFile(3)  # 3 tracks: melody, chords, drums
    time = 0

    # Setup tracks
    for track in range(3):
        midi.addTempo(track, time, tempo)
        # Set different instruments for each track
        if track == 0:
            midi.addProgramChange(track, 0, 0, 0)  # Piano for melody
        elif track == 1:
            midi.addProgramChange(track, 0, 0, 48)  # Strings for chords
        else:
            midi.addProgramChange(track, 9, 0, 0)  # Standard drum kit

    # Get scale notes and total duration
    scale = get_scale(key, scale_type, octaves=2, base_octave=base_octave)
    total_duration = 0

    # Track 0: Melody
    prev_note_idx = None
    melody_times = []  # Store melody note timings for synchronization

    for i in range(length):
        if prev_note_idx is not None:
            possible_indices = list(range(max(0, prev_note_idx - 3), 
                                       min(len(scale), prev_note_idx + 4)))
            note_idx = random.choice(possible_indices)
        else:
            note_idx = random.randint(0, len(scale) - 1)

        note, octave = scale[note_idx]
        midi_note = note_to_midi_number(note, octave)
        prev_note_idx = note_idx

        duration = random.choice([0.5, 1, 2])
        velocity = random.randint(85, 110)

        midi.addNote(0, 0, midi_note, time, duration, velocity)
        melody_times.append((time, duration))
        time += duration
        total_duration = max(total_duration, time)

    # Track 1: Chords (if enabled)
    if enable_chords:
        chord_time = 0
        measures = int(total_duration / 4)  # 4 beats per measure

        while chord_time < total_duration:
            progression = get_chord_progression(scale_type)

            for chord_idx in progression:
                if chord_time >= total_duration:
                    break

                # Build triad from scale degrees
                root_idx = (chord_idx - 1) * 2
                third_idx = root_idx + 2
                fifth_idx = root_idx + 4

                if root_idx < len(scale):
                    root_note, root_oct = scale[root_idx]
                    third_note, third_oct = scale[third_idx % len(scale)]
                    fifth_note, fifth_oct = scale[fifth_idx % len(scale)]

                    # Add chord notes
                    for note, oct in [(root_note, root_oct), (third_note, third_oct), (fifth_note, fifth_oct)]:
                        midi_note = note_to_midi_number(note, oct)
                        midi.addNote(1, 0, midi_note, chord_time, 4, 70)

                chord_time += 4  # One bar per chord

    # Track 2: Drums (if enabled)
    if enable_drums:
        measures = int(total_duration / 4)  # 4 beats per measure
        drum_pattern = generate_drum_pattern(measures=measures)

        for drum, beat_time in drum_pattern:
            if beat_time < total_duration:  # Only add drum hits within the melody duration
                midi.addNote(2, 9, DRUM_NOTES[drum], beat_time, 0.25, 100)

    # Write file
    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)