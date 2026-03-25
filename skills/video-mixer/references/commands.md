# Video Mixer Commands

This skill forwards commands to the repository's `VideoMixerSkillHandler`.

## `listTransitions`

No payload is required.

Example:

```json
{}
```

## `mix`

Required fields:

- `output`: output video path
- `clips`: array of clip objects

Clip object fields:

- `path`: source video path
- `duration`: optional trim duration in seconds
- `transition`: optional transition name such as `fade`, `wipeleft`, `wiperight`, `zoomin`, `circleopen`, `pixelize`
- `transitionDuration`: optional transition duration in seconds

Optional top-level fields:

- `resolution`: `[width, height]`
- `transitionEnabled`: boolean
- `audioEnabled`: boolean
- `audioFadeIn`: number
- `audioFadeOut`: number
- `textOverlays`: array of overlay objects
- `colorCorrection`: object

Text overlay fields:

- `text`
- `startTime`
- `duration`
- `x`
- `y`
- `fontsize`
- `fontcolor`
- `fontPath`

Example:

```json
{
  "output": "E:\\mix\\result.mp4",
  "clips": [
    {
      "path": "E:\\mix\\clip1.mp4",
      "transition": "fade",
      "transitionDuration": 1.0
    },
    {
      "path": "E:\\mix\\clip2.mp4",
      "transition": "wipeleft",
      "transitionDuration": 0.8
    }
  ],
  "resolution": [1920, 1080],
  "transitionEnabled": true,
  "audioEnabled": true
}
```

## `thumbnail`

Required fields:

- `videoPath`
- `output`

Optional fields:

- `timestamp`
- `width`

## `saveConfig`

Required fields:

- `config`
- `output`

## `loadConfig`

Required fields:

- `configPath`
