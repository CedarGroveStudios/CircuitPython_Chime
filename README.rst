Introduction
------------

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/CedarGroveStudios/CircuitPython_Chime/workflows/Build%20CI/badge.svg
    :target: https://github.com/CedarGroveStudios/CircuitPython_Chime/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

A CircuitPython class for generating wind chime and bell sounds using `synthio`.

The CedarGrove CircuitPython Chime class provides `synthio` note overtones and envelopes developed from
a combination of tubular chime algorithms and empirical (practical) models. Three chime voices are included
in the class (``Voice.Tubular``, ``Voice.Bell``, and ``Voice.Perfect``) as well as selectable chime
and striker materials. The ``Scales`` class contains a library of common wind chime and bell scales
in a collection of Scientific Pitch Notation (SPN) lists.

The ``Chime`` class is instantiated after an MCU board-specific audio output object is defined. The
audio output object can be an Analog DAC or PWM GPIO pin as well as an I2S DAC output (as in the
simpletest example). Chime notes are then played by the ``Chime.strike(root_note, amplitude)`` function.


Dependencies
------------
This class depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `CedarGrove CircuitPython_MIDI_Tools <https://github.com/CedarGroveStudios/CircuitPython_MIDI_Tools>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Usage Example
-------------

.. code-block:: python

    import time
    import board
    import random
    import audiobusio
    import audiomixer
    from cedargrove_chime import Chime, Scale, Voice, Material, Striker

    # Instantiate I2S output and mixer buffer for synthesizer
    audio_output = audiobusio.I2SOut(
        bit_clock=board.D12, word_select=board.D9, data=board.D6
    )
    mixer = audiomixer.Mixer(
        sample_rate=11020, buffer_size=4096, voice_count=1, channel_count=1
    )
    audio_output.play(mixer)
    mixer.voice[0].level = 1.0

    # Instantiate the chime synth with mostly default parameters
    chime = Chime(mixer.voice[0], scale=Scale.HarryDavidPear)

    # Play scale notes sequentially
    for index, note in enumerate(chime.scale):
        chime.strike(note, 1)
        time.sleep(0.4)
    time.sleep(1)

    while True:
        # Play randomly
        for count in range(random.randrange(10)):
            chime.strike(random.choice(chime.scale), 1)
            time.sleep(random.randrange(1, 3) * 0.6)

        time.sleep(random.randrange(1, 10) * 0.5)

The ``Chime`` class was also used for an IoT Weather Chime project using the ESB32-S2 that plays "windless" electronic chimes in accordance with the outdoor wind speed: https://github.com/CedarGroveStudios/Weather_Chimes

Documentation
-------------
API documentation for this library can be found in `Cedargrove_Chime_API <https://github.com/CedarGroveStudios/CircuitPython_Chime/blob/main/media/pseudo_rtd_cedargrove_chime.pdf>`_.

.. image:: https://github.com/CedarGroveStudios/CircuitPython_Chime/blob/main/media/chime_api_page3.png


Planned Updates
---------------
* Limit the practical chime overtones to a specified frequency range such as 300Hz to 3000Hz.
* Provide additional chime scales.
* Update the Overtones class to include aluminum, wood, and brass.

Acknowledgements and Thanks
---------------------------
* Lee Hite, '`Tubular Bell Chimes Design Handbook`' for the analysis of tubular chime physics and overtones.
* C. McKenzie, T. Schweisinger, and J. Wagner, '`A Mechanical Engineering Laboratory Experiment
  to Investigate the Frequency Analysis of Bells and Chimes with Assessment`' for the analysis
  of bell overtones.
* Liz Clark, '`Circle of Fifths Euclidean Synth with synthio and CircuitPython`' Adafruit Learning Guide
  for the waveform and noise methods.
* Todd Kurt for fundamentally essential `synthio` hints, tricks, and examples
  (https://github.com/todbot/circuitpython-synthio-tricks).

Also, special thanks to Jeff Epler and Adafruit for the comprehensive design and implementation
of the amazing CircuitPython `synthio` module.
