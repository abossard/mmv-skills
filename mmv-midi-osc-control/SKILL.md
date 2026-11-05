---
name: mmv-midi-osc-control
description: Control Magic Music Visuals from MIDI, OSC, MIDI clock, Ableton Live and other apps, and send OSC out. Covers adding MIDI/OSC sources, feature indices (CC, Note Velocity, Beat Clock, Iterator Notes), Learn, controller mapping (MIDImix, Launchpad), OSCSender, playlist control by MIDI/OSC, and what Magic cannot do (no Ableton Link, NDI, DMX, MIDI out) with working bridges. Use when wiring controllers, DAWs, beat sync or external apps to Magic.
---

# MIDI, OSC, clock, Ableton

Prerequisite: [mmv-core](../mmv-core/SKILL.md). MIDI/OSC input and OSCSender need the Performer edition.

## Sources

```python
root = b.build()
root = m.add_midi_in(root, "IAC Driver MagicBus", channel=1, name="DAW")      # Layer "DAW": notes and CC on channel 1
root = m.add_midi_in(root, "IAC Driver MagicBus", channel=0, name="Clock")    # Layer "Clock": Beat Clock arrives on channel 0
root = m.add_midi_in(root, "MIDI Mix", channel=1, name="MIX")
root = m.set_osc_in(root, 8000)                                                # Layer "OSC In" on UDP 8000
root = m.add_global(root, "Fader1", 0, source="midi:MIX:Control Change:19", mods=[("Smooth", 0.1)])
root = m.add_global(root, "Beat",   0, source="midi:Clock:Beat Clock:Beat")
root = m.add_global(root, "BPM",    0, source="midi:Clock:Beat Clock:Clock BPM", mods=[("Scale", 120)])
root = m.add_global(root, "Pad1",   0, source="midi:MIX:Note Velocity:9", mods=[("Trigger", 0.5), ("Wrap", 2)])  # toggle
root = m.add_global(root, "Fx",     0, source="osc:/1/fader1")
```

(`Builder.glob` resolves sources against the template Layers; MIDI/OSC Layers are added after `build()`, so link those with `add_global`/`edit_param` as above. All of this checked offline with `magicproj check`; OSC input also verified live.)

## MIDI features (feature index, subFeature)

0 Velocity, 1 Pitch Bend, 2 Note Number, 3 Control Change (CC#), 4 Aftertouch (note), 5 Channel Pressure, 6 Program Change, 7 Note Velocity (note), 8 Beat Clock (0 beat, 1 /2, 2 /3, 3 /4, 4 Clock BPM), 9 CC Number, 10 Iterator Notes. All scaled 0..1 (value/127); the playlist sees raw 0..127. Channel 0 = global channel (Beat Clock). Velocity, Note Number and CC Number cannot be learned; choose by hand.

Idioms: momentary pad to toggle = Note Velocity -> Trigger 0.5 -> Wrap 2. Held-note switch = Note Velocity -> Threshold 0.01. Piano keys = Iterator (88, Offset 21) + `Iterator Notes`.

## OSC in

- Source = Layer on an OSC Track (UDP port). Feature text = address; `"/addr 1"` picks argument 1. Value used as sent (no 0..1 normalisation).
- Verified: project with `Builder(osc_in=17011)`, param `osc:/probe/r`, `mmv_verify.py --live --yes --osc /probe/r=1.0 --osc-port 17011` gives red 143 vs 0 at value 0.
- Common ports: 8000 (Magic's default), 9000/9001 and 11111 (typical for other OSC tools). Pick a free port with `lsof -nP -iUDP:PORT`.

## OSC out

`OSCSender` module: `IP Addr.`, `Port`, `Message`, `Value`. One IP/port per project. Sends only on change: a constant never arrives, so jitter by 0.001 for 2 s after load if the receiver needs the initial value. Put senders in their own scene drawn as a scene module from every shown scene (they run only while drawn).

## What Magic does NOT have (checked in the binary)

| Missing | Do this instead |
|---|---|
| Ableton Link | Link is tempo sync only. Run Live (a Link peer) and send MIDI clock to the IAC Driver: Live > Settings > Link, Tempo & MIDI > MIDI Ports: enable IAC Driver Out "Sync". Magic reads Beat Clock (feature 8) on channel 0 of that device. Or analyse the audio (kick Globals). For Link-only devices use a bridge that outputs MIDI clock or OSC (untested here). |
| MIDI out (only for MIDI file playback) | send OSC out and convert elsewhere |
| Art-Net / sACN / DMX | OSCSender to a bridge (QLC+ via OSC, or a small script); QLC+ accepts OSC input |
| NDI | NDISyphon: NDI -> Syphon -> `SyphonClient`; for output Syphon -> NDI sender |
| MTC / SMPTE | none |
| Direct param control from OSC addresses | link params to OSC Layer, one address per param |

## Ableton Live workflow

1. IAC Driver (Audio MIDI Setup > MIDI Studio): create a bus, e.g. "MagicBus".
2. Live: MIDI Ports: IAC Out "Track" on for notes/CC from MIDI tracks, "Sync" on for clock.
3. Magic: add a MIDI source on that device. Clock via Beat Clock, section triggers via notes, macro knobs via CC (map Live macros to a MIDI clip or Max for Live LFO/envelope devices that send CC).
4. Audio reactive: Live master out to BlackHole (multi-output) and read it as `Source 0`.
5. Scene changes: Playlist MIDI/OSC config (below).

## Playlist control

`PlaylistMidiConfig`: global command (entry number = value 0..127 or OSC first arg), prev/next commands, per-entry commands. Unset = -1. Edit through `magicproj` XML or the UI (Learn). Beat Clock, Pitch Bend, Iterator Notes cannot trigger playlist changes.

## Controllers

Typical controllers: Akai MIDImix (faders to Globals, buttons to Note Velocity toggles), Novation Launchpad (grid pads to playlist entries or scene slots), IAC bus from a DAW. Learn: click a linked param's Source/Feature label > Start > move control > Use.

More detail and gotchas: [references/control.md](references/control.md).
