# Control details

## Modifier param and bypass by MIDI/OSC

`ValueOperator` attrs `paramLayerID/Feature/SubFeature/FeatureString` drive a modifier's number; `bypassLayerID/...` drive its bypass; `bypassMidiToggle="1"` = Use As Toggle; `paramMidiScale` = Param Range factor. No bundled sample uses them (all -1). Use a Global instead: link the Global to MIDI, use `x` in an Expression elsewhere.

## Global command vs per-entry

- Global command: "entry number = value". Good for a program-change fader.
- Per-entry: one note per scene (Launchpad grid).
- Prev/Next: two buttons; wraps and skips disabled entries.

## Latency

MIDI/OSC arrive per frame; at 60 fps expect up to 16 ms plus one frame per Global hop. Link controller values straight to params for tight response; use Globals for shared logic.

## Learn limits

Learn detects the command you send (per the guide: most MIDI messages, OSC addresses, Beat Clock on channel 0; turn that off with "Ignore Beat Clock For MIDI Learn"). It cannot find Velocity, Note Number, CC Number: pick those by hand.

## Disabling

Window > Disable All MIDI/OSC Input if a MIDI driver hangs. Learn is unavailable then.

## Bridges worth knowing (not verified in this session)

- Synesthesia -> OSC `/audio/beat/onbeat` into Magic OSC In (link a Global to `osc:/audio/beat/onbeat`).
- TouchOSC/Lemur: OSC faders `/1/faderN`.
- Processing + Syphon: a Processing sketch publishes a Syphon server, Magic reads it with `SyphonClient`; control back over OSC.
- Link to MIDI clock: Ableton Live itself, or a Link peer script writing MIDI clock to an IAC port.
