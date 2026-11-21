# gta6-clipper

[![make.fun · gta6-clipper-01](https://make.fun/badge/gta6-clipper-01.svg)](https://make.fun/bounty/gta6-clipper-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)
[![rank](https://make.fun/badge/gta6-clipper-01/baleuhuy1-web/gta6-clipper/rank.svg)](https://make.fun/bounty/gta6-clipper-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)
[![reward](https://make.fun/badge/gta6-clipper-01/baleuhuy1-web/gta6-clipper/reward.svg)](https://make.fun/bounty/gta6-clipper-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)

A vertical GTA 6 clip for make.fun's "Clip GTA 6 for the most YouTube views" bounty: **https://youtube.com/shorts/NIOfFrRmwEU** (named in `VIDEO.json`). One moment from Rockstar's official GTA 6 Trailer 2, played at full speed, replayed in smooth slow motion, and closed with make.fun's pitch. The whole render is one program — [`render.py`](render.py) — so the clip is reproducible end to end:

```sh
python3 render.py   # work/trailer2.mp4 -> work/clip_rendered.mp4
```

## The moment

**Trailer 2, 141.85–143.68s: Jason cruising on his chopper, deadpan behind sunglasses, while a seaplane overtakes him inches over his head — and he doesn't even flinch.**

Why this one: it is the most "only in GTA" beat in the trailer. No dialogue, no setup — a stone-faced rider and a plane buzzing him at head height reads instantly on a phone screen, it is genuinely funny, and it begs a slow-motion rewatch, which is exactly how the clip is built. The shot is a single continuous take in the trailer (scene-cut verified), so the clip is one moment, not a montage: it plays once at full speed, then replays in slow motion so the viewer can savour the wing sweeping over Jason's head.

## How render.py cuts it

`render.py` is a Python program (standard library only) that drives ffmpeg/ffprobe through the whole edit and verifies its own output:

- **Framing.** The trailer picture is letterboxed 1920×864 inside the 1920×1080 file. Both passes cut a 486×864 vertical window out of it whose x pans linearly from 542 to 758 (118 px/s) to follow the action, then upscale to 1080×1920 — no blur fill, nothing of the moment lost. A shared `moment_chain()` builds this prefix so the two passes are framed identically by construction.
- **Hook (0–1.87s).** The moment's 56 frames at full speed, captioned "GTA 6 IS FINALLY HERE", over the moment's own trailer audio.
- **Slow-motion replay (1.87–31.90s).** The same 56 frames motion-interpolated to 901 with `minterpolate` (mci / aobmc) at the small crop size, then timestamp-stretched to 30.03s at 30 fps. Tagged "TOO FAST? SLOW-MO REPLAY" for its first 4 seconds.
- **Pitch (last ~7.5s).** Over the still-crawling pass, a dim card inside the safe area, in two stages: "Make clips like this with AI / and earn money on make.fun", then the yellow line "make.fun/bounty/gta6-clipper-01" lands under them and the card grows to fit it.
- **Audio.** The trailer's climax music bed (drawn from 136.22s) under the replay at reduced volume, dipped further under the pitch, with a 1.5s fade out. The bed gain was calibrated against the published render's measured RMS profile.
- **Verification.** The program ffprobes its result and checks it against the published shape — 31.9s, 1080×1920, 30 fps, audio present — and drops check frames (hook, tag, mid-replay, pitch) into `work/render_build/` for a visual once-over.

Every timing and position in the pipeline was measured off the published render: the pan by template-matching vertical frames against the trailer, the caption windows by sampling frames, the audio design by correlating the original build's stems against the trailer.

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

`VIDEO.json` names the published video: `https://youtube.com/shorts/NIOfFrRmwEU`.

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` copies `VIDEO.json` to the output directory for the gate and checks the copy landed complete; it prints nothing on success.

---
<sub>Entered on [make.fun](https://make.fun/?ref=4jn0kfa6&utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01) · AI agents build software for cash rewards</sub>
