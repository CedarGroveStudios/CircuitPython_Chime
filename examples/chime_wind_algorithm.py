# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`chime_wind_algorithm`
===============================================================================
A test of a wind chime wind speed algorithm.

* Author(s): JG for Cedar Grove Maker Studios

Implementation Notes
--------------------
**Software and Dependencies:**
* CedarGrove CircuitPython_Chime:
  https://github.com/CedarGroveStudios/CircuitPython_Chime
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import time
import random
import board
import audiobusio
import audiomixer
from simpleio import map_range
from cedargrove_chime import Chime, Scale

# Instantiate I2S output and mixer buffer for synthesizer
audio_output = audiobusio.I2SOut(
    bit_clock=board.D12, word_select=board.D9, data=board.D6
)
mixer = audiomixer.Mixer(
    sample_rate=11020, buffer_size=4096, voice_count=1, channel_count=1
)
audio_output.play(mixer)

# Set the overall output volume level
mixer.voice[0].level = 0.8

# Instantiate the chime synth with mostly default parameters
chime = Chime(mixer.voice[0], scale=Scale.HarryDavidPear)

# Play scale notes sequentially at full volume
for index, note in enumerate(chime.scale):
    chime.strike(note, 1)
    time.sleep(0.4)
time.sleep(1)

WIND_SPEED = 0

while True:
    """Play a randomized chime note sequence in proportion to wind speed.
    It's assumed that the chime tubes are mounted in a circle and that no more
    than half the tubes will sound when the striker moves due to wind. The
    initial chime tube note (chime_index[0]) is selected randomly from
    chime.scale. The initial struck note will be followed by adjacent notes
    either to the right or left as determined by the random direction variable.
    The playable note indices are contained in the chime_index list. Chime note
    amplitude and the delay between note sequences is proportional to
    the wind speed."""

    """Populate the chime_index list with the initial note then add the
    additional adjacent notes."""
    chime_index = []
    chime_index.append(random.randrange(len(chime.scale)))

    direction = random.choice((-1, 1))
    for count in range(1, len(chime.scale) // 2):
        chime_index.append((chime_index[count - 1] + direction) % len(chime.scale))

    """Randomly select the number of notes to play in the sequence."""
    notes_to_play = random.randrange(len(chime_index) + 1)

    """Play the note sequence with a random delay between each."""
    note_amplitude = map_range(WIND_SPEED, 0, 50, 0.4, 1.0)
    for count in range(notes_to_play):
        chime.strike(chime.scale[chime_index[count]], note_amplitude)
        time.sleep(random.randrange(10, 60) * 0.01)  # 0.10 to 0.50 seconds

    """Delay the next note sequence inversely based on wind speed plus a
    random interval."""
    time.sleep(map_range(WIND_SPEED, 0, 50, 2.0, 0.01) + (random.random() / 2))
