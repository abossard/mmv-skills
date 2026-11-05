# Output notes

## Frame path

Magic window (graphics resolution) -> Syphon texture (same size) -> client app. No extra scaling inside Magic. Window resizing only changes the preview unless "Use size of Magic Window" is chosen in Graphics Resolution.

## Why a frame can look wrong

| Symptom | Cause | Fix |
|---|---|---|
| Client shows nothing | `videoSharing` off, name mismatch, Magic not rendering the scene (playlist shows another scene) | `grab --server NAME`; check playlist entry |
| Stretched | project resolution differs from the mapping canvas | match sizes, do not scale in the client |
| Black bars | aspect bars in Magic window (fixed res in a window of another aspect) | irrelevant to Syphon, only the preview |
| Flicker / tearing on projector | vsync off or double-sync with the mapping app | Magic Vertical Sync on, mapping app output at display refresh |
| Dropped frames | heavy scene, Preview Window open, status text update | close Preview Window, Module Text Update Speed Off |

## Multi-machine

Syphon is local. Between machines use NDI (NDISyphon / OBS NDI) or capture cards. Send control (OSC) over the network instead of video where possible.

## Related user material

Syphon: syphon.v002.info. NDISyphon and OBS Syphon plugins: see their project pages.
