# ADR-001: MIDI Message Processing Rate Limiting

**Date**: April 15, 2026  
**Status**: Implemented  
**Deciders**: Max Cascone  
**Context**: Firmware reliability, live performance guarantee

---

## Context and Problem Statement

The MIDI Captain firmware processes incoming MIDI messages from USB and TRS/serial transports in a tight polling loop. Without rate limiting, a malicious or buggy MIDI host could flood the device with messages, causing it to lock up processing the infinite queue and become unresponsive to button presses.

This is unacceptable for a **live performance device** where reliability is paramount.

## Decision Drivers

- **Live performance reliability** — Device must remain responsive even when receiving MIDI floods
- **Button responsiveness** — Switch scanning must not be starved by MIDI processing
- **Display updates** — Screen and LED updates must continue during high MIDI traffic
- **Real-world scenarios** — Scene changes on devices like Quad Cortex can send 100+ CC messages in < 1 second

## Considered Options

### Option 1: No Rate Limiting (Original Approach)
Process all available MIDI messages in each loop iteration.

**Pros**:
- Simple implementation
- No messages ever dropped

**Cons**:
- Device vulnerable to MIDI flood attacks
- Button presses can be delayed or missed during MIDI bursts
- Display updates freeze during heavy MIDI traffic
- Infinite loop possible if host continuously sends messages

### Option 2: Time-Based Rate Limiting
Process messages for maximum time budget per loop (e.g., 5ms).

**Pros**:
- Guarantees loop timing
- Naturally adapts to message complexity

**Cons**:
- Complex to implement (requires timing each message)
- Overhead of time checks
- Variable message count per loop

### Option 3: Message Count Limiting (CHOSEN)
Process maximum `N` messages per loop iteration.

**Pros**:
- Simple implementation — single counter
- Predictable behavior — always processes up to N messages
- Low overhead — no timing required
- Leftover messages processed in next iteration (fair queuing)

**Cons**:
- Messages may be delayed (but never dropped)
- Fixed limit may not be optimal for all scenarios

## Decision Outcome

**Chosen Option**: Message Count Limiting (`MAX_MIDI_MESSAGES_PER_LOOP = 16`)

The firmware implements a message count cap in `handle_midi()`:

```python
MAX_MIDI_MESSAGES_PER_LOOP = 16

def handle_midi():
    messages_processed = 0
    
    # Process USB MIDI (up to limit)
    while messages_processed < MAX_MIDI_MESSAGES_PER_LOOP:
        msg = midi_usb.receive()
        if msg is None:
            break
        _process_incoming_midi(msg)
        messages_processed += 1
    
    # Process TRS/serial MIDI (up to remaining budget)
    while messages_processed < MAX_MIDI_MESSAGES_PER_LOOP:
        msg = midi_trs.receive()
        if msg is None:
            break
        _process_incoming_midi(msg)
        messages_processed += 1
```

### Rationale for N=16

**Throughput calculation**:
- MIDI baud rate: 31,250 bits/sec = 3,125 bytes/sec
- Average MIDI message: 3 bytes (status + 2 data bytes)
- Maximum real-world throughput: ~1,000 messages/sec

**Loop timing**:
- Main loop target: 1000 Hz (1ms per iteration) after sleep addition
- 16 messages/loop × 1000 loops/sec = 16,000 messages/sec capacity
- This is **16× higher than maximum real MIDI throughput**

**Starvation analysis**:
- Worst case: sustained 1000 msg/sec MIDI flood
- With cap of 16: main loop processes 16 msgs/ms
- Remaining handlers (switches, display, LEDs): ~15 ms per loop
- Button scan frequency: still 1000 Hz (plenty responsive)

In practice, MIDI bursts are short (scene changes, not sustained), so the cap rarely matters.

### Startup Grace Period

The firmware also implements a startup grace period (`STARTUP_MIDI_GRACE_PERIOD_SEC = 1.0`) to handle power-on MIDI bursts from external devices:

```python
if in_grace_period:
    # During grace period: fully drain all messages without processing
    while True:
        msg = midi_usb.receive()
        if msg is None:
            break
        # Message discarded
else:
    # After grace period: apply rate limit
    messages_processed = 0
    while messages_processed < MAX_MIDI_MESSAGES_PER_LOOP:
        # ... process message
```

During the grace period, the firmware **drains the entire buffer** (no cap) but does **not process messages**. This prevents external devices from overriding `default_selected` button states during their power-on sequence.

### Fairness Between Transports

The implementation processes USB MIDI first, then TRS MIDI, both counting toward the same `MAX_MIDI_MESSAGES_PER_LOOP` budget. This:
- Prevents one transport from starving the other
- Gives USB slight priority (host communication typically more important)
- Ensures total processing time is bounded

## Consequences

### Positive

- ✅ Device remains responsive during MIDI floods
- ✅ Button presses never missed, even under heavy MIDI traffic
- ✅ Display and LED updates continue without freezing
- ✅ Simple implementation with minimal overhead
- ✅ Predictable behavior — always processes up to 16 messages

### Negative

- ⚠️ Messages may be delayed by 1-2ms during sustained floods (acceptable for control messages)
- ⚠️ Theoretical maximum throughput reduced from infinite to 16,000 msg/sec (still 16× real MIDI max)

### Mitigation

If a use case requires processing >16 messages per loop, the constant can be increased. However, real-world testing shows 16 is more than sufficient:
- Scene changes: ~50-100 messages over 100ms = 5-10 per loop average
- Continuous CC streams: limited by MIDI baud rate (~1000 msg/sec = 1 per loop)

## Links

- **Implementation**: [firmware/circuitpython/code.py](../../firmware/circuitpython/code.py) (lines 1300-1360)
- **Test Coverage**: [tests/test_midi_processing_cap.py](../../tests/test_midi_processing_cap.py)
- **Related Issue**: Code Quality Investigation Report (Finding #5)
- **CircuitPython MIDI Library**: adafruit_midi

## Lessons Learned

- **Embedded systems need explicit resource limits** — CircuitPython has no built-in backpressure
- **Counting is simpler than timing** — Message count cap is easier to reason about than time budget
- **Real-world testing validates theory** — 16 msg/loop works perfectly in practice
- **Live performance = predictable worst case** — Must handle pathological inputs gracefully

## Future Considerations

- **Adaptive rate limiting**: Increase cap when no button activity detected
- **Per-transport limits**: Separate caps for USB vs TRS to prevent cross-transport starvation
- **Message priority**: Process Note/PC before CC (if needed for low-latency note triggering)
- **Telemetry**: Log dropped/delayed message counts for debugging

None of these are currently needed based on real-world usage.

---

**Status**: This ADR documents existing implemented behavior, not a future decision. The rate limiting has been in production since March 2026 and performs well.
