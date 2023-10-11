# SPDX-FileCopyrightText: Copyright (c) 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`cedargrove_chime_simpletest`
===============================================================================
A test of the cedargrove_chime wind chime synthesizer module.

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
from cedargrove_chime import Chime, Scale

# Instantiate I2S output and mixer buffer for synthesizer
audio_output = audiobusio.I2SOut(
    bit_clock=board.D12, word_select=board.D9, data=board.D6
)
mixer = audiomixer.Mixer(
    sample_rate=11020, buffer_size=4096, voice_count=1, channel_count=1
)
audio_output.play(mixer)
mixer.voice[0].level = 1.0

# Instantiate the chime synthesizer with mostly default parameters
chime = Chime(mixer.voice[0], scale=Scale.HarryDavidPear)

# Play scale notes sequentially
for index, note in enumerate(chime.scale):
    chime.strike(note, 1)
    time.sleep(0.4)
time.sleep(1)

while True:
    # Play scale notes randomly
    for count in range(random.randrange(10)):
        chime.strike(random.choice(chime.scale), 1)
        time.sleep(random.randrange(1, 3) * 0.6)

    time.sleep(random.randrange(1, 10) * 0.5)
