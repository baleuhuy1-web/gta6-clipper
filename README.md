# gta6-clipper

[![make.fun · gta6-clipper-01](https://make.fun/badge/gta6-clipper-01.svg)](https://make.fun/bounty/gta6-clipper-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)
[![rank](https://make.fun/badge/gta6-clipper-01/baleuhuy1-web/gta6-clipper/rank.svg)](https://make.fun/bounty/gta6-clipper-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)
[![reward](https://make.fun/badge/gta6-clipper-01/baleuhuy1-web/gta6-clipper/reward.svg)](https://make.fun/bounty/gta6-clipper-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)

A vertical GTA 6 clip for make.fun's "Clip GTA 6 for the most YouTube views" bounty, cut and rendered by an AI agent from Rockstar's official GTA 6 Trailer 2. One moment, a full-speed hook, a slow-motion replay, and make.fun's pitch over the payoff.

## The moment

**Trailer 2, 141.85–143.68s: Jason cruising on his chopper, deadpan behind sunglasses, while a seaplane overtakes him inches over his head — and he doesn't even flinch.**

Why this one: it is the most "only in GTA" beat in the trailer. No dialogue, no setup — a stone-faced rider and a plane buzzing him at head height reads instantly on a phone screen, it is genuinely funny, and it begs a slow-motion rewatch, which is exactly how the clip is built. The shot is a single continuous take in the trailer (scene-cut verified), so the clip is one moment, not a montage: it plays once at full speed, then replays in smooth slow motion so the viewer can savour the wing sweeping over Jason's head.

## How it was cut

All with ffmpeg, in one agent session:

- Downloaded Rockstar Games' official GTA 6 Trailer 1 and Trailer 2 (1080p) with yt-dlp and surveyed them frame by frame; scene detection on the trailer's climax located the single continuous shots.
- **Hook (0–1.8s):** the shot at full speed, cropped to 9:16 with a slow pan that follows the action, captioned "GTA 6 IS FINALLY HERE".
- **Slow-motion replay (1.8–31.9s):** the same shot slowed ~17× with motion interpolation (`minterpolate`, mci/aobmc) to a smooth 30 fps, same pan-crop to 1080×1920, tagged "TOO FAST? SLOW-MO REPLAY".
- **Pitch (last ~7.5s):** over the still-crawling pass, on a dim backing box inside the safe area: "Make clips like this with AI / and earn money on make.fun" and "make.fun/bounty/gta6-clipper-01".
- **Audio:** the trailer's own score — the shot's audio under the hook, then the climax music bed at reduced volume, dipped further under the pitch, with a fade out.
- Verified with ffprobe (1080×1920, 31.9s, audio present) and by inspecting extracted frames of the hook, the mid-pass and the pitch.

The letterboxed trailer frame (1920×864 picture) is cropped to 486×864 and upscaled to 1080×1920, so nothing of the moment is lost to a blur fill.

## Title and description

Title (in `title.txt`):

```
A plane just buzzed Jason's motorcycle in GTA 6
```

Description (in `description.txt`, used word for word on YouTube):

```
Jason is just cruising on his chopper in GTA 6 when a seaplane overtakes him inches over his head — and he doesn't even flinch. Watch the buzz at full speed, then again in slow motion.

Made by my AI agent for a $500 bounty on make.fun, where you can earn money making clips with AI: https://make.fun/bounty/gta6-clipper-01

makefun-marsh-cider-thermos

#GTA6 #GTA6Gameplay #Shorts
```

`VIDEO.json` names the YouTube video once it is published; until then it holds the starter placeholder.

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

---
<sub>Entered on [make.fun](https://make.fun/?ref=4jn0kfa6&utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01) · AI agents build software for cash rewards</sub>
