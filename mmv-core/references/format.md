# .magic file format (Magic 3.0b6)

Evidence tags: (saved) Magic's own saves, 36 bundled samples plus other projects; (binary) strings/disassembly of `Magic`; (guide) User's Guide; (live) read back from a running Magic via Syphon.

## Container

- 3 header bytes then a zlib stream (`78 9c`). Magic writes a random header each save and never checks it (live: generated files with header `L*h` load). Decode: `zlib.decompress(data[3:])`.
- XML is UTF-8, CRLF in saves. Any well-formed XML with the same elements loads (live). Round-trips are semantic, not byte-identical. Magic renumbers all ids on save.
- Magic refuses newer projects with "Magic v... is needed to open the project" (binary). Keep `version="1.5"` and `actualVersion="3"`.

## Skeleton (element order)

```
Project  looping playlistChangesTabs videoSharing videoSharingName videoSharingWidth videoSharingHeight
         fixedMagicSize fontSize audioFilePanelHeight version="1.5" actualVersion="3"
  RenderSettings   width height fps duration(frames) usePlaylist format quality outputFolder outputFile   (movie export only)
  PlaylistMidiConfig  layerID feature subFeature featureString prev*/next* ... (-1 = unset)
  SoundFiles / AudioFiles version="2"       (audio/MIDI files: SoundFile+AudioFile filename offset isMuted isSoloed)
  Tracks   Track id channel isInput name [deviceName] [isMidi] [isOSC] [soundFileIndex audioFileIndex]
  Layers   Layer name id trackID gain gainVisible        ("Sources" in the UI)
  Scenes   Scene name id isPostProcessing excludedFromPostProcessing keepInGfxMem
             Root/Node pluginName="Magic" magicNode="1"   Children/Child id  (= scene outputs, top pin first)
             Nodes/Node ...
  Playlists/Playlist/Scene  id style duration sceneDuration enabled layerID feature subFeature featureString
  Tabs/Tab/Node  x y id expanded annotation annotationVisible annotationName   (one Tab per scene, editor positions)
  TabsVisible/TabVis sceneID
  SceneTreeItems/SceneTreeItem id group [name expanded]
  Globals/InputValue ...
```

## Node and InputValue

```xml
<Node pluginName="ColorHSB" magicNode="0" disabled="0" bypassed="0" bypassParamUsed="0" powerParamUsed="0" dontRestart="0" id="12">
  <Children><Child id="11"/></Children>                 <!-- input pins, first = top pin -->
  <InputValues>
    <InputValue name="Hue" id="40" globalsUseID="1" linked="1" open="1" layerID="2147483646"
                feature="5" subFeature="0" featureVersion="1" value="0">
      <ValueOperators>
        <ValueOperator type="1" param="0.3" bypassed="0" paramLayerID="-1" paramFeature="-1" paramSubFeature="-1"
                       paramFeatureString="" bypassLayerID="-1" bypassFeature="-1" bypassSubFeature="-1"
                       bypassMidiToggle="0" bypassFeatureString="" paramMidiScale="1" paramString="x"/>
      </ValueOperators>
    </InputValue>
```

- Scene module: `Node pluginName=<scene name> sceneID=<Scene@id>`, no `layerID`. SceneInput: `pluginName="SceneInput" sceneInputID=<id of the scene it sits in>`.
- External ISF: add `isfFilename="/abs/path.fs"`; `pluginName` = module name (file stem) (live).
- `Node id`, `InputValue id`, `Track id`, `Layer id`: keep unique project wide (Builder uses one counter).
- File params: `value` = path relative to the project, plus `absoluteFilename` (guide, saved). Absolute paths in `value` work (live: Model, GLSLShader).

## Source link (any InputValue, including Globals)

| linked | layerID | meaning |
|---|---|---|
| 0 | -1 | manual `value` |
| 1 | -1 | no source: input 0, modifiers compute ("calc") |
| 1 | 2147483646 | Global; `feature` = that Global's InputValue id |
| 1 | 2147483645 | Internals; `feature` = index below |
| 1 | a `Layer id` | that source; the Track decides audio, MIDI (`isMidi`) or OSC (`isOSC`, address in `featureString`) |

Unlinked values still carry the first Layer id and feature 0; harmless.

Audio `feature`: 0 Volume, 1 Freq. Range, 2 Best Pitch, 3 Tone. Freq. Range `subFeature`: 0 20-80 Hz, 1 80-320, 2 320-1.2k, 3 1.2k-5k, 4 5k-20k, 5 Custom (`extraFeature1/2` = low/high cutoff), 6 Iterator Freqs. All 0..1.

MIDI `feature`: 0 Velocity, 1 Pitch Bend, 2 Note Number, 3 Control Change (`subFeature` = CC#), 4 Aftertouch (note), 5 Channel Pressure, 6 Program Change, 7 Note Velocity (`subFeature` = note), 8 Beat Clock (sub 0 beat, 1 /2, 2 /3, 3 /4, 4 Clock BPM), 9 CC Number, 10 Iterator Notes. (3, 6, 7, 10 confirmed in saves; others from the binary label table.)

Internals `feature`: 0/2 graphics width, 1/3 graphics height, 4 Playlist Entry #, 5 Playback Time, 6 Graphics FPS, 7 Iteration #, 8 Total Iterations, 10 Audio/MIDI Playing, 11 Playback Seeked.

## Modifiers (`ValueOperator type`)

0 Gate, 1 Scale, 2 Offset, 3 Power, 4 Smooth, 5 Wrap, 6 Random, 7 Ramp, 8 Sine, 9 Triangle, 10 Threshold, 11 Average, 12 Peak, 13 Exponent, 14 Clamp, 15 Step, 16 Increase, 17 Trigger, 18 Invert, 19 Hold, 20 Delay, 21 Expression, 22 RandomTrigger. Applied in listed order, each takes the previous output as input. `paramString` is the ExprTk source for type 21 (`x` input, `y` previous output, Globals by name, case-insensitive), `"x"` for others.

## Params of modules

- Native modules: names in [module-catalog.md](module-catalog.md).
- ISF modules: name = `LABEL` else `NAME` with first letter capitalised; `point2D` -> `<Name> X`, `<Name> Y`; `color` -> `<Name> R/G/B/A` (0,0,0,0 without DEFAULT); `audio`/`audioFFT` inputs are params named after their LABEL/NAME (`Source`, `FFT`, `Wave`; value = Layer id, `-1` none) and an `audio` input also adds `Overwrite`; shaders using `TIME` (`TIMEDELTA` counts) get `Speed`, saved as `Speed (M)` when an input's NAME or LABEL contains "speed" (Bad TV, and two custom shaders in saved projects; the exact rule is Magic's); every module has `Power`, modules with an `image` input also `Bypass`. The JSON header is the first `/*{...}*/` comment, `//` lines may precede it. `magicproj.isf_params(text, module=True)` follows these rules and matches names and defaults of all 187 bundled ISF modules.
- ISF `long`: stored value = 0-based INDEX into VALUES/LABELS (live: Blend Mode 9 = Screen; God Rays default 10 is saved as 1). The header's DEFAULT is the VALUES entry; `isf_params` converts it to the index.
- ISF `bool`: 0/1. `image` inputs are pins, in header order.
- Params are clamped to their range silently.

## Coordinates (guide, live)

y -1 (bottom) .. 1 (top); x edge = aspect ratio (1.778 at 16:9); `Polygon Sides 4` at Scale 1 is a square as tall as the frame. 2D ISF output is a plane that fills the frame and can be scaled, rotated and translated like any module.

## Syphon and OSC attributes

- `videoSharing="1"` turns Syphon out on, `videoSharingName` is the server name (client sees "<name> - Magic"), `videoSharingWidth/Height` is the graphics resolution (live).
- OSC in: `Track isInput="1" isOSC="1" channel=<UDP port> name="Open Sound Control"` plus a `Layer`. Params link to that Layer with the address in `featureString` (live: `/probe/r` moved a colour).
- OSC out: `OSCSender` modules (`IP Addr.`, `Port`, `Message`, `Value`), one IP and port per project.
