# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`cedargrove_chime`
===============================================================================
A CircuitPython class for generating wind chime and bell sounds using synthio.
https://github.com/CedarGroveStudios/CircuitPython_Chime

Acknowledgement and thanks to:
* Lee Hite, 'Tubular Bell Chimes Design Handbook' for the analysis of tubular
  chime physics and overtones.
* C. McKenzie, T. Schweisinger, and J. Wagner, 'A Mechanical Engineering
  Laboratory Experiment to Investigate the Frequency Analysis of Bells and Chimes
  with Assessment' for the analysis of bell overtones;
* Liz Clark, 'Circle of Fifths Euclidean Synth with synthio and CircuitPython'
  for the waveform and noise methods;
* Todd Kurt for fundamentally essential synth hints, tricks, and examples
  (https://github.com/todbot/circuitpython-synthio-tricks).

Also, special thanks to Jeff Epler for the comprehensive design and implementation
of the amazing CircuitPython synthio module.

* Author(s): JG for Cedar Grove Maker Studios

Implementation Notes
--------------------
**Software and Dependencies:**
* CedarGrove CircuitPython_MIDI_Tools:
  https://github.com/CedarGroveStudios/CircuitPython_MIDI_Tools
  and in the CircuitPython Community Bundle
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import synthio
import ulab.numpy as np
from cedargrove_midi_tools import name_to_note


class Voice:
    """The predefined synth voices. Bell is a single-capped tube
    with empirical overtones. Perfect is a dual-capped tube with algorithmically
    generated overtones equal to the length-related harmonics. Tubular is a
    traditional open-ended tube chime with empirical non-harmonic overtones."""

    Bell = "bell"
    Perfect = "perfect"
    Tubular = "tubular"


class Scale:
    """A collection of common wind chime musical note scales from
    Tubular Bell Chimes Design Handbook, Lee Hite."""

    Westminister = ["G#5", "E5", "F#5", "B4"]
    Pentatonic = ["C5", "D5", "E5", "G5", "A5"]
    CNine = ["C5", "E5", "G5", "A#5", "D6"]
    HavaNegila = ["C5", "C#5", "E5", "F5", "G5", "G#5"]
    CorinthianBellsA = ["A4", "B4", "C#5", "E5", "F#5", "A5"]
    CorinthianBellsB = ["B4", "C#5", "D#5", "F5", "G#5", "A#5"]
    CorinthianBellsC = ["C4", "D4", "E4", "G4", "A4", "C5"]
    CorinthianBellsEb = ["D#4", "F4", "G4", "A#4", "C5", "D#5"]
    CorinthianBellsG = ["G4", "A4", "B4", "D5", "E5", "G5"]
    Whittington = ["E5", "F#5", "G5", "A5", "B5", "C#6", "D6"]
    Canterbury = ["D5", "E5", "F#5", "G5", "A5", "B5"]
    Trinity = ["D5", "G5", "A5", "B5", "C6", "D6"]
    Winchester = ["C5", "D5", "E5", "F5", "G5", "A5"]
    StMichaels = ["F5", "G5", "A5", "A#5", "C6", "D6", "E6", "F6"]
    HappyBirthday = ["C6", "D6", "E6", "F6", "G6", "A6", "A#6", "B6", "C7"]

    # Other wind chimes measured in-field
    HarryDavidPear = ["F#5", "G#5", "B5", "C6", "E6", "G6"]  # tubular steel
    CeramicTurtles = []  # ceramic bells
    CeramicBells = []  # ceramic bells
    Biplane = ["G3", "B3", "D4", "G4"]  # tubular copper
    SandCast = ["F6", "A#6"]  # brass bells


class Material:
    """The attack time, attack level, and release time for various chime/bell
    materials."""

    SteelEMT = [0.02, 1.0, 2.0]
    Ceramic = [0.10, 1.0, 0.8]  # has different harmonics than SteelEMT
    Wood = [0.15, 1.0, 1.0]  # has different harmonics than SteelEMT
    Copper = [0.02, 1.0, 2.5]  # may have different harmonics than SteelEMT
    Aluminum = [0.02, 0.9, 1.3]
    Brass = [0.02, 1.0, 2.5]


class Striker:
    """The attack time and attack level ratios for various striker materials."""

    Metal = [0.00, 1.0]
    Plexiglas = [0.01, 1.0]
    SoftWood = [0.05, 1.0]
    HardWood = [0.02, 1.0]


class Overtones:
    """The voice overtone frequency factors and relative amplitude factors of
    each. The root note is Overtones.Chime[0]. Other overtones follow in the
    list. For example, the primary overtone is Overtones.Chime[1]. To avoid
    note distortion, the sum of overtone amplitude factors should equal 1.0
    or less."""

    """Bell overtones were measured empirically but fall close to the
    theoretical single-capped tubular harmonics where overtones are the
    odd harmonics."""
    Bell = [(1.00, 0.8), (1.48, 0.19), (1.35, 0.01), (1.72, 0.0)]

    """Perfect overtones: the theoretical harmonics of a dual-capped tube."""
    Perfect = [
        (1.00, 0.6),
        (2.00, 0.2),
        (3.00, 0.1),
        (4.00, 0.05),
        (5.00, 0.05),
        (6.00, 0.0),
        (7.00, 0.0),
    ]

    """Tubular overtones were measured empirically. They are not equal to
    theoretical dual-capped tubular overtones or harmonics."""
    Tubular = [
        (1.00, 0.6),
        (2.76, 0.2),
        (5.40, 0.1),
        (8.93, 0.1),
        (11.34, 0.0),
        (18.64, 0.0),
        (31.87, 0.0),
    ]


class Chime:
    """A synthesizer for wind chime or bell sounds using synthio."""

    def __init__(
        self,
        audio_out,
        scale=Scale.CNine,
        material=Material.SteelEMT,
        striker=Striker.Metal,
        voice=Voice.Tubular,
        scale_offset=0,
        loudness=0.5,
        debug=False,
    ):
        """Create the chime oscillator waveform, note envelope, overtones,
        scale, and to instantiate the synthesizer.

        :param bus audio: An instantiated audio object to receive the output
        audio stream, typically an I2S connection, analog DAC output pin, or
        PWM output pin. No default.
        :param list scale: The list of playable chime notes in Scientific
        Pitch Notation (SPN). Each element of the scale list is a single SPN
        string such as “A#4” for the fourth-octave A# (Bb) note. The
        Chime.Scale class contains a collection of chime scale lists. Defaults
        to Scale.CNine.
        :param list material: A list of note envelope parameters (attack time,
        attack level, release time) based on the chime construction material.
        The Chime.Material class consists of presets for a variety of
        materials. Defaults to Material.SteelEMT.
        :param list striker: A list of note envelope parameter ratios (attack
        time, attack level) based on the striker construction material. The
        ratios are used to adjust chime note envelope properties. The
        Chime.Striker class consists of presets for a variety of materials.
        Defaults to Striker.Metal.
        :param str voice: A string representing the pre-defined synth voices.
        The Chime.Voice class contains presets for: Voice.Bell, a single-capped
        tube with empirical overtones; Voice.Perfect, a dual-capped tube with
        algorithmically generated overtones equal to the length-related
        harmonics, and Voice.Tubular, a traditional open-ended tube chime with
        empirical non-harmonic overtones. Defaults to Voice.Tubular.
        :param int scale_offset: A positive or negative integer value of note
        pitch half-steps to offset the pitch of the scale. Defaults to 0 (no
        scale pitch offset).
        :param float loudness: A normalized floating point value for output
        amplitude, ranging from 0.0 to 1.0. Defaults to 0.5 (one-half volume).
        :param bool debug: A boolean value to enable debug print messages.
        Defaults to False (no debug print messages).
        """

        self._debug = debug
        self._voice = voice
        self._material = material
        self._striker = striker
        self._scale_offset = scale_offset  # half-steps
        self._loudness = loudness

        # Set default ADSR envelope settings
        self._note_envelope = synthio.Envelope(
            attack_time=material[0] + striker[0],
            attack_level=material[1] * striker[1],
            decay_time=0.0,
            release_time=material[2],
            sustain_level=1.0,
        )

        # Set voice overtones
        if self._voice == Voice.Bell:
            self._overtones = Overtones.Bell
        elif self._voice == Voice.Perfect:
            self._overtones = Overtones.Perfect
        else:
            # For Voice.Tubular
            self._overtones = Overtones.Tubular

        # Create scale table
        self._scale = []
        for index, note in enumerate(scale):
            self._scale.append(
                min(max(name_to_note(note) + self._scale_offset, 0), 127)
            )
        if self._debug:
            print(f"scale={scale} self._scale={self._scale} list created")

        """Create a single-cycle (one-lambda) sine waveform table to act as
        the oscillator."""
        wave_size = 128  # 512 recommended by todbot
        wave_rate = 11020  # 22050 recommended by todbot
        wave_max_value = int(self._loudness * 31000)  # 0-32767 (signed 16-bit)

        self._wave_sine = np.array(
            np.sin(np.linspace(0, 2 * np.pi, wave_size, endpoint=False))
            * wave_max_value,
            dtype=np.int16,
        )

        # Instantiate the synthesizer
        self.synth = synthio.Synthesizer(
            sample_rate=wave_rate, waveform=self._wave_sine
        )
        audio_out.play(self.synth)

    @property
    def scale(self):
        """The chime scale list in SPN."""
        return self._scale

    @scale.setter
    def scale(self, new_scale=Scale.CNine):
        self._scale = []
        for index, note in enumerate(new_scale):
            self._scale.append(
                min(max(name_to_note(note) + self._scale_offset, 0), 127)
            )
        if self._debug:
            print(f"scale={new_scale} self._scale={self._scale} list created")

    @property
    def loudness(self):
        """The current loudness value."""
        return self._loudness

    @loudness.setter
    def loudness(self, new_loudness=0.5):
        self._loudness = new_loudness

    def strike(self, root_note=49, amplitude=0):
        """Strike the chime or bell. The note envelope and overtone values are
        determined by the chime/bell and striker materials.
        :param int root_note: The root_note MIDI integer value; ranges from
        0 to 128. Defaults to 49 (A4).
        :param float amplitude: The amplitude of the note; range 0.0 to 1.0.
        Defaults to 0.0 (muted)."""

        root_note_freq = synthio.midi_to_hz(root_note)
        adjusted_amplitude = amplitude * self._loudness

        self._notes = (
            synthio.Note(
                root_note_freq * self._overtones[0][0],
                amplitude=adjusted_amplitude * self._overtones[0][1],
                envelope=self._note_envelope,
            ),
            synthio.Note(
                root_note_freq * self._overtones[1][0],
                amplitude=adjusted_amplitude * self._overtones[1][1],
                envelope=self._note_envelope,
            ),
            synthio.Note(
                root_note_freq * self._overtones[2][0],
                amplitude=adjusted_amplitude * self._overtones[2][1],
                envelope=self._note_envelope,
            ),
            synthio.Note(
                root_note_freq * self._overtones[3][0],
                amplitude=adjusted_amplitude * self._overtones[3][1],
                envelope=self._note_envelope,
            ),
        )

        self.synth.press(self._notes)
        self.synth.release(self._notes)
