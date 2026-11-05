# Show patterns

## A. One-scene performance bus

`Program` scene: Gen A and Gen B subtrees (each a scene module), `Mix Amount` = `GenMix` Global, FX `Look` scene module, `Master`/`Blackout` Transparency at the end. MIDI: crossfader to `GenMix`, faders to FX amounts, pads to scene slot. No scene changes = no hitch.

## B. Song-per-entry playlist

Entry per track with MIDI note per entry (Launchpad row). `sceneDuration` large (or auto-advance off). Transition 0 for beat-synced cuts, 1-2 s for song changes. Each entry's scene stays cheap; share assets via scene modules.

## C. Karaoke / lyrics overlay

Separate `Lyrics` scene (Text or SyphonClient lyrics app), LumaKey over Program; draw it from Master so playlist changes do not drop it.

## D. External renderer + Magic as glue

Blender, Godot or Resolume render, Magic receives via SyphonClient, adds audio-reactive FX and outputs Syphon again. Control path: OSC out from Magic (`OSCSender`) to the renderer; video path: Syphon back.

## E. Rehearsal without audio

`magicproj.add_audio(root, wav, loop=True)` plus `mmv_verify --play --frames 6`, or drive Globals with OSC (`--osc /addr=0.8 --osc-port N`). Keep the rehearsal project separate from the show project.

## Recovery

- Magic crash: reopen the last `.magic`; auto-backup in temp (`MagicBackups`); settings in `~/Library/Application Support/MAGIC/MAGIC_1_0.xml` (contains a key; never share).
- Dead links after hardware change: re-route the Source (Input Sources > Change Source Device/File); module links stay because they name the Layer.
- Black output after load: wrong playlist entry, Power off on the Magic module, scene not in the playlist, Syphon client name mismatch.
