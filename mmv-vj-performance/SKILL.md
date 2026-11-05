---
name: mmv-vj-performance
description: Run Magic Music Visuals live - playlist entries, transitions, auto-advance, scene switching by MIDI/OSC, Preview Mode for live editing, frame-rate budget and GPU/VRAM management, safe-load and crash-recovery habits, strobe safety, and a pre-show checklist. Use when preparing a gig, structuring a set across scenes, fixing dropped frames or audio lag, or setting up unattended startup.
---

# VJ workflow and performance

Prerequisite: [mmv-core](../mmv-core/SKILL.md). Control mapping: [mmv-midi-osc-control](../mmv-midi-osc-control/SKILL.md).

## Set structure

- Few scenes, each a complete look; shared stuff in scene modules (one `Look` bus, one `Controls`/`OSC Out` scene). Every scene costs VRAM.
- One Master scene holds the always-on parts (blackout, overlay, OSC out) and draws the Program scene via a scene module. Users switch looks inside Program by playlist or by a `Slot` Global with InputSelector/Mix.
- Controls are Globals in 0..1: `Gain`, `Master`, `Blackout`, `Buildup`, `Drop`, per-effect amounts. All MIDI/OSC maps to Globals, never to module params, so remapping hardware is one place.
- Two ways to change looks: Playlist (separate scenes, transitions, MIDI per entry) or a crossfade bus inside one scene (no reload, one GPU budget). For a live set prefer the bus for beat-synced changes, the playlist for song changes.

## Playlist (XML: `Playlists/Playlist/Scene`)

`style` 0 none / 1 crossfade / 2 additive dissolve, `duration` transition seconds (default 2), `sceneDuration` auto-advance seconds (default 30), `enabled`. `magicproj.set_playlist(root, names, seconds, transition, style)`. Transitions draw two scenes: double cost, so keep them shorter than the entry and avoid them at 60 fps limit. Auto-advance (Shift+Space) is not millisecond exact live. Disabled entries are skipped by next/prev and auto-advance but reachable by command. Select entry by MIDI value (global command) or per-entry notes.

## Live editing safely

- Scene > Preview Mode: edits go to the Preview Window; only the Playlist changes the Magic window. Preview Window can cost up to 50% fps; close it when not editing.
- Window > Disable All Keyboard Input stops accidental keys (until restart). Better: no keyboard, MIDI/OSC only.
- Auto-Save every 5 minutes and Auto-Backup write to the temp dir (`MagicBackups`). Keep a hand copy of the show file before the gig (Save As with date).
- Always keep a "Safe" scene: a simple, cheap look at playlist entry 0 you can punch to if something breaks.
- Never add or delete modules in the displayed scene during a show.

## Frame-rate budget

- Target 60 fps at the output resolution; if the FPS line drops, perceived audio sync drops too. `Cmd+I` shows status.
- Biggest levers: lower graphics resolution (Shift+Cmd+G), bypass idle effects via Global thresholds, fewer scenes in VRAM (turn off Load All Scenes Into Graphics Memory only if switching hitches are acceptable), Module Text Update Speed Off (big on macOS), Antialias off or MSAA 2x, reduce Iterator counts, cheaper shaders (see mmv-effects-color cost list).
- Throttling default 1 ms; Vertical Sync on; do not mirror displays; extended desktop with black background.
- Clock source: audio output device by default (tight AV sync). If no output device, untick `Use Audio Output As Clock Source`.
- On a 120 Hz MacBook display the frame rate ran about 115-120 fps (frame time 8.7 ms measured via a Dt Global). Per-frame decays differ by display; use `Dt`-based expressions.

## Audio and sync

- Use a loopback input (BlackHole 2ch) or an interface, not the laptop mic. Multi-Output device in Audio MIDI Setup to hear it while Magic reads it.
- Projector/TV processing off ("game mode"), highest refresh; display lag dominates AV sync.
- MIDI clock via IAC for tempo-locked effects; kick Globals as fallback (see audio skill).

## Strobe and safety

Limit full-frame flashes to <= 3 per second unless the venue and audience are informed; add a `Blackout` Global multiplying the final bus, and a `StrobeLimit` expression (Hold 0.34 s). Provide a MIDI panic button that sets `Blackout` 1 and `Strobe` 0.

## Pre-show checklist

1. Project saved under a dated name; assets collected (File > Collect Assets) so paths resolve on the show machine.
2. Resolution and fullscreen display set; test pattern shown on every output.
3. Audio device selected; meters move at soundcheck level; `Gain` set.
4. MIDI/OSC devices connected before launching Magic; Learn-check each control; Disable All MIDI/OSC Input off.
5. FPS >= 60 on the heaviest scene while audio plays.
6. Preview Window closed, Module Text Update Speed Off, Keyboard input disabled if hardware control is solid.
7. System: no sleep/screensaver, power connected, notifications and updates off, Wi-Fi off if not needed.
8. Backup project on USB; second machine ready if the show matters.
9. Safe scene reachable with one button.

## Unattended startup

Window > Magic Window Options: Start In Fullscreen, Display To Use, Start Auto-Advance; put the `.magic` file in the login items. Magic does not take command line flags (`open -a MagicBeta file.magic` is the supported launch).

See [references/show-patterns.md](references/show-patterns.md) for set structures.
