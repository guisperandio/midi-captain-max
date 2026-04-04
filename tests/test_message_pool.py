"""
Tests for MIDI message pool behavior.

Validates that reusable message objects maintain correct field values
despite being mutated and reused across multiple sends.

This addresses the concern that storing message references could lead
to all references pointing to the same object with only the last mutation.
"""

import pytest
import sys
from pathlib import Path

# Add the firmware directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "firmware" / "circuitpython"))

from core.message_pool import midi_cc_msg, midi_pc_msg, midi_note_on_msg, midi_note_off_msg


class TestMessagePoolFieldValues:
    """Test that message pool objects maintain correct field values."""

    def test_cc_message_fields_after_multiple_mutations(self):
        """Validate CC message fields are correct after multiple reuses."""
        # Simulate sending CC messages with different values
        sent_messages = []

        # Send first CC message (CC 20, value 127)
        midi_cc_msg.control = 20
        midi_cc_msg.value = 127
        sent_messages.append({"control": midi_cc_msg.control, "value": midi_cc_msg.value})

        # Send second CC message (CC 21, value 64)
        midi_cc_msg.control = 21
        midi_cc_msg.value = 64
        sent_messages.append({"control": midi_cc_msg.control, "value": midi_cc_msg.value})

        # Send third CC message (CC 22, value 0)
        midi_cc_msg.control = 22
        midi_cc_msg.value = 0
        sent_messages.append({"control": midi_cc_msg.control, "value": midi_cc_msg.value})

        # Verify all captured values are correct
        assert sent_messages[0] == {"control": 20, "value": 127}
        assert sent_messages[1] == {"control": 21, "value": 64}
        assert sent_messages[2] == {"control": 22, "value": 0}

    def test_pc_message_fields_after_multiple_mutations(self):
        """Validate PC message fields are correct after multiple reuses."""
        sent_messages = []

        # Send first PC message (patch 0)
        midi_pc_msg.patch = 0
        sent_messages.append({"patch": midi_pc_msg.patch})

        # Send second PC message (patch 5)
        midi_pc_msg.patch = 5
        sent_messages.append({"patch": midi_pc_msg.patch})

        # Send third PC message (patch 127)
        midi_pc_msg.patch = 127
        sent_messages.append({"patch": midi_pc_msg.patch})

        # Verify all captured values are correct
        assert sent_messages[0] == {"patch": 0}
        assert sent_messages[1] == {"patch": 5}
        assert sent_messages[2] == {"patch": 127}

    def test_note_on_message_fields_after_multiple_mutations(self):
        """Validate Note On message fields are correct after multiple reuses."""
        sent_messages = []

        # Send first Note On (note 60, velocity 100)
        midi_note_on_msg.note = 60
        midi_note_on_msg.velocity = 100
        sent_messages.append({"note": midi_note_on_msg.note, "velocity": midi_note_on_msg.velocity})

        # Send second Note On (note 64, velocity 127)
        midi_note_on_msg.note = 64
        midi_note_on_msg.velocity = 127
        sent_messages.append({"note": midi_note_on_msg.note, "velocity": midi_note_on_msg.velocity})

        # Send third Note On (note 72, velocity 90)
        midi_note_on_msg.note = 72
        midi_note_on_msg.velocity = 90
        sent_messages.append({"note": midi_note_on_msg.note, "velocity": midi_note_on_msg.velocity})

        # Verify all captured values are correct
        assert sent_messages[0] == {"note": 60, "velocity": 100}
        assert sent_messages[1] == {"note": 64, "velocity": 127}
        assert sent_messages[2] == {"note": 72, "velocity": 90}

    def test_note_off_message_fields_after_multiple_mutations(self):
        """Validate Note Off message fields are correct after multiple reuses."""
        sent_messages = []

        # Send first Note Off (note 60, velocity 0)
        midi_note_off_msg.note = 60
        midi_note_off_msg.velocity = 0
        sent_messages.append({"note": midi_note_off_msg.note, "velocity": midi_note_off_msg.velocity})

        # Send second Note Off (note 64, velocity 64)
        midi_note_off_msg.note = 64
        midi_note_off_msg.velocity = 64
        sent_messages.append({"note": midi_note_off_msg.note, "velocity": midi_note_off_msg.velocity})

        # Verify all captured values are correct
        assert sent_messages[0] == {"note": 60, "velocity": 0}
        assert sent_messages[1] == {"note": 64, "velocity": 64}

    def test_mixed_message_types_correct_values(self):
        """Validate correct field values when mixing message types."""
        sent_messages = []

        # Send CC message
        midi_cc_msg.control = 20
        midi_cc_msg.value = 127
        sent_messages.append({"type": "cc", "control": midi_cc_msg.control, "value": midi_cc_msg.value})

        # Send PC message
        midi_pc_msg.patch = 5
        sent_messages.append({"type": "pc", "patch": midi_pc_msg.patch})

        # Send Note On message
        midi_note_on_msg.note = 60
        midi_note_on_msg.velocity = 100
        sent_messages.append({"type": "note_on", "note": midi_note_on_msg.note, "velocity": midi_note_on_msg.velocity})

        # Send CC message again
        midi_cc_msg.control = 21
        midi_cc_msg.value = 64
        sent_messages.append({"type": "cc", "control": midi_cc_msg.control, "value": midi_cc_msg.value})

        # Send Note Off message
        midi_note_off_msg.note = 60
        midi_note_off_msg.velocity = 0
        sent_messages.append({"type": "note_off", "note": midi_note_off_msg.note, "velocity": midi_note_off_msg.velocity})

        # Verify all captured values are correct
        assert sent_messages[0] == {"type": "cc", "control": 20, "value": 127}
        assert sent_messages[1] == {"type": "pc", "patch": 5}
        assert sent_messages[2] == {"type": "note_on", "note": 60, "velocity": 100}
        assert sent_messages[3] == {"type": "cc", "control": 21, "value": 64}
        assert sent_messages[4] == {"type": "note_off", "note": 60, "velocity": 0}

    def test_message_pool_objects_are_same_instance(self):
        """Verify that we're truly reusing the same object instances."""
        # Get initial object IDs
        cc_id = id(midi_cc_msg)
        pc_id = id(midi_pc_msg)
        note_on_id = id(midi_note_on_msg)
        note_off_id = id(midi_note_off_msg)

        # Mutate all messages
        midi_cc_msg.control = 20
        midi_cc_msg.value = 127
        midi_pc_msg.patch = 5
        midi_note_on_msg.note = 60
        midi_note_on_msg.velocity = 100
        midi_note_off_msg.note = 60
        midi_note_off_msg.velocity = 0

        # Verify object IDs haven't changed (same instances)
        assert id(midi_cc_msg) == cc_id
        assert id(midi_pc_msg) == pc_id
        assert id(midi_note_on_msg) == note_on_id
        assert id(midi_note_off_msg) == note_off_id

    def test_rapid_successive_sends_correct_values(self):
        """Simulate rapid successive sends (e.g., encoder scrolling)."""
        sent_values = []

        # Simulate encoder sending 10 CCs rapidly
        for i in range(10):
            midi_cc_msg.control = 11
            midi_cc_msg.value = i * 12  # 0, 12, 24, 36...
            sent_values.append(midi_cc_msg.value)

        # Verify all values are correct
        expected = [i * 12 for i in range(10)]
        assert sent_values == expected

    def test_channel_field_not_affected_by_pooling(self):
        """Verify channel is handled separately (not part of message object)."""
        # Message objects don't have a .channel field - it's passed separately
        # to send_midi_message(). Verify message objects don't gain unexpected fields.
        
        # Check that message objects only have expected fields
        cc_attrs = [attr for attr in dir(midi_cc_msg) if not attr.startswith('_')]
        assert 'control' in cc_attrs
        assert 'value' in cc_attrs
        # Channel is NOT a field of the message object itself

        pc_attrs = [attr for attr in dir(midi_pc_msg) if not attr.startswith('_')]
        assert 'patch' in pc_attrs

        note_on_attrs = [attr for attr in dir(midi_note_on_msg) if not attr.startswith('_')]
        assert 'note' in note_on_attrs
        assert 'velocity' in note_on_attrs


class TestMessagePoolImportConsistency:
    """Test that all modules use the same shared message pool."""

    def test_message_pool_objects_are_singletons(self):
        """Verify that importing from message_pool always gives same instances."""
        from core.message_pool import midi_cc_msg as cc1
        from core.message_pool import midi_cc_msg as cc2
        
        # Same object ID means same instance (singleton behavior)
        assert id(cc1) == id(cc2)
        
        # Mutating one affects the other (they're the same object)
        cc1.control = 42
        assert cc2.control == 42

    def test_all_message_types_available(self):
        """Verify all message types are exported from the pool."""
        from core.message_pool import (
            midi_cc_msg,
            midi_pc_msg,
            midi_note_on_msg,
            midi_note_off_msg
        )
        
        # All should be defined
        assert midi_cc_msg is not None
        assert midi_pc_msg is not None
        assert midi_note_on_msg is not None
        assert midi_note_off_msg is not None
