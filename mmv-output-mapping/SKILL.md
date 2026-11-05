---
name: mmv-output-mapping
description: Get Magic Music Visuals output to screens, projectors and other apps - Syphon/Spout server output, graphics resolution and aspect, fullscreen on a chosen display, feeding projection-mapping and media-server apps (Millumin, MadMapper, Resolume, VDMX, OBS), NDI bridging, edge blending and calibration patterns, movie export, and receiving other apps via SyphonClient. Use when planning outputs, mapping a surface, diagnosing resolution or sync issues, or building a calibration scene.
---

# Output, projection mapping, Syphon

Prerequisite: [mmv-core](../mmv-core/SKILL.md).

## What Magic does and does not do

- Does: one Magic window (windowed or fullscreen on any display), Syphon (macOS) / Spout (Windows) output, movie/PNG export, SyphonClient/SpoutReceiver input (also from another Magic instance).
- Does not: warp/keystone/edge-blend/mesh-map surfaces, output NDI, DMX or Art-Net, drive multiple independent outputs from one project. Do mapping in a mapping app fed over Syphon. Verified: Magic 3.0b6 binary has no mapping/NDI strings.

## Syphon out (verified live)

- Project attrs: `videoSharing="1"`, `videoSharingName="My Scene"`, `videoSharingWidth/Height` = graphics resolution. Builder: `Builder(syphon="My Scene", size=(1920,1080))`; or `magicproj set f.magic -o g.magic --syphon on --syphon-name "My Scene" --size 1920x1080`. GUI: Window > Magic Window Options > Syphon Output; server name option next to it.
- Clients list it as `<name> - Magic` (default `Main Server - Magic`). Two Magic instances cannot run (single instance), so one server per machine; to split outputs, route one Syphon frame into a mapping app and slice there.
- The frame is the graphics resolution (fixed or window size, Shift+Cmd+G), not the window size. Use fixed resolution (`fixedMagicSize="1"`) for stable Syphon size.
- Frames are bottom-up for some readers (syphon-python); the `magicproj grab` helper flips them.
- Status bar shows `s` while Syphon is on (Cmd+I toggles the status text).

## Choosing resolution

| Target | Resolution |
|---|---|
| Single 16:9 projector / TV | 1920x1080 (60 fps) |
| Mapping app downstream | one canvas for the whole surface layout, e.g. 3840x1080 for two side-by-side projectors; avoid > GPU max output (Help > Graphics Info) |
| Square LED wall | 1080x1080 or the panel pixel size |
| Sketch / rehearsal | 1280x720 |
| Heavy shaders | render 1280x720 and scale up in the mapping app, or add a `Resolution` module before the Magic output |

Coordinates scale to height: design for the aspect, keep important content inside +/-1 in y and +/-(aspect) in x, leave 5% margin for mapping crops.

## Mapping-app workflow

1. Build `mapping_test_pattern.py` scene (checkerboard, color grid, 4 colored corners, cross, size label), run it at the intended canvas size.
2. Mapping app (Millumin, MadMapper, Resolume and VDMX all take Syphon input): add Syphon input `<name> - Magic`, create outputs/surfaces, warp, blend, mask.
3. Replace the test scene with the show; do not change resolution afterwards (it rescales the Syphon texture).
4. Edge blending: overlap 10-20% in the mapping app and leave gamma at 1.8-2.2 per projector; Magic only supplies the content.
5. Lock display settings: extended desktop (never mirror), black background, projector game mode (no processing).

`scripts/mapping_test_pattern.py OUT.magic --size 3840x1080 --name "Wall"` generates the calibration scene (verified: opens, renders corners, grid, label).

## Fullscreen and displays

Cmd+F cycles main display > each extra display > windowed. Window > Magic Window Options > Enter Fullscreen On Display > [n], Start In Fullscreen, Display To Use, Always Hide Mouse Over Fullscreen. Exit Fullscreen For Other Apps is on by default; turn it off for shows. Two same-size displays side by side can be spanned. These are app preferences, not project settings.

## Receiving other apps

`SyphonClient` `Server` = `"<server> - <app>"` (examples: `S - Synesthesia`, `<host> (VirtualDJ) - NDISyphon`, a Blender or Godot Syphon sender). Missing server = draws nothing; composite over a safe background. Servers visible now: `magicproj grab` error text lists them.

## NDI, Spout, other protocols

- NDI in: NDISyphon app turns NDI streams into Syphon servers (for example with VirtualDJ's NDI output). NDI out: Syphon into OBS (Syphon plugin) or Millumin/Resolume NDI output.
- OBS: add a Syphon Client source `Main Server - Magic` for streaming or recording.
- Windows: Spout equivalent (`SpoutReceiver` module, `Spout Output`; named in the User's Guide, not in the macOS catalog).

## Movie export

File > Export Movie (Cmd+U); not real time, ignores live audio/MIDI/OSC and VideoCapture, so only file-driven scenes export. `RenderSettings` (width, height, fps, duration in frames, format code, quality 0..10 = CRF 28..18). Codecs: H.264 (also 4:2:2/4:4:4), ProRes 422/422 HQ/4444 (alpha), Motion JPEG, PNG sequence. Width/height multiples of 4 for mp4/mov. For pre-rendered loops into a mapping app use ProRes or Hap-encoded video via `VideoFile` (Hap plays best).

## Verify an output

`mmv_verify.py proj.magic --live --yes --out f.png` grabs the Syphon frame exactly as a client sees it: check size, colours, corners. Latency: Syphon adds about one frame; display lag of the projector dominates audio sync (see mmv-vj-performance).
