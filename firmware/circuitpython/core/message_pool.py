"""
MIDI Captain MAX - Shared Message Pool

Centralized reusable MIDI message objects to eliminate allocation overhead.

These message objects are mutable and reused across all send operations to reduce
memory allocation and garbage collection pressure in CircuitPython's constrained
memory environment.

Usage:
    from core.message_pool import midi_cc_msg, midi_pc_msg
    
    midi_cc_msg.control = 20
    midi_cc_msg.value = 127
    send_midi_message(midi_cc_msg, channel=0)

Author: Max Cascone
Date: 2026-04-04
"""

from adafruit_midi.control_change import ControlChange
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# Global reusable MIDI message objects
# These are mutable and should be updated before each send
midi_cc_msg = ControlChange(0, 0)       # Reusable ControlChange message
midi_pc_msg = ProgramChange(0)          # Reusable ProgramChange message
midi_note_on_msg = NoteOn(0, 0)         # Reusable NoteOn message
midi_note_off_msg = NoteOff(0, 0)       # Reusable NoteOff message
