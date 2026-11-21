#!/usr/bin/env python3
"""Render pipeline for the gta6-clipper-01 entry, "A plane just buzzed Jason's
motorcycle in GTA 6" (https://youtube.com/shorts/NIOfFrRmwEU).

This program rebuilds the published 31.9 s vertical Short from Rockstar's
official GTA 6 Trailer 2 (`work/trailer2.mp4`) using only the Python standard
library plus ffmpeg/ffprobe subprocess calls:

    python3 render.py                 # writes work/clip_rendered.mp4
    python3 render.py --out out.mp4   # writes somewhere else

The clip is one moment — Trailer 2, 141.85 s in, where a seaplane buzzes
Jason's chopper at head height and he does not flinch — presented three ways:

  1. Hook   (0.00–1.87 s)  the moment at full speed, captioned
                           "GTA 6 IS FINALLY HERE", over the moment's own audio.
  2. Replay (1.87–31.90 s) the same 56 frames stretched to 901 frames with
                           ffmpeg's `minterpolate` motion interpolation
                           (mci / aobmc), tagged "TOO FAST? SLOW-MO REPLAY"
                           for its first 4 seconds, over the trailer's climax
                           music bed at reduced volume.
  3. Pitch  (last ~7.5 s)  still inside the replay: a dim card fades in over
                           the crawling pass with make.fun's pitch in two
                           stages — the two white lines first, then the
                           yellow bounty URL under them.

Every number below was measured off the published render (`work/clip.mp4`):
the pan was recovered by template-matching vertical frames against the
trailer, the caption timings by sampling frames, and the audio design by
correlating the original build's stems (`work/aseg1.m4a`, `work/aseg2.m4a`)
against the trailer. The trailer picture is letterboxed 1920x864 inside the
1920x1080 file; the vertical frame is a 486x864 window panning across it at
118 px/s, upscaled to 1080x1920.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Measured parameters of the published clip
# --------------------------------------------------------------------------

REPO = Path(__file__).resolve().parent
WORK = REPO / "work"
SOURCE = WORK / "trailer2.mp4"

MOMENT_START = 141.85          # seconds into Trailer 2
FPS = 30
HOOK_FRAMES = 56               # full-speed pass: 56 frames = 1.8667 s
REPLAY_FRAMES = 901            # slow-motion pass: 901 frames = 30.0333 s
HOOK_DUR = HOOK_FRAMES / FPS
REPLAY_DUR = REPLAY_FRAMES / FPS
TOTAL_DUR = HOOK_DUR + REPLAY_DUR          # 31.9 s

PICTURE_Y = 108                # letterbox offset of the 1920x864 picture
CROP_W, CROP_H = 486, 864      # vertical window cut from the picture
PAN_X0, PAN_V = 542, 118       # crop x = PAN_X0 + PAN_V * t (t = s into moment)
OUT_W, OUT_H = 1080, 1920

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
HOOK_TEXT = "GTA 6 IS FINALLY HERE"
TAG_TEXT = "TOO FAST? SLOW-MO REPLAY"
TAG_DUR = 4.0                  # seconds into the replay
CAPTION_Y = 215

PITCH_LINES = ("Make clips like this with AI", "and earn money on make.fun")
PITCH_URL = "make.fun/bounty/gta6-clipper-01"
PITCH_START = 22.5             # seconds into the replay (last ~7.5 s overall)
PITCH_URL_DELAY = 1.5          # the yellow URL follows the white lines
BOX_X, BOX_Y, BOX_W = 40, 605, 1000
BOX_H1, BOX_H2 = 395, 500      # the card grows when the URL line lands

BED_START = 136.22             # trailer climax the music bed is drawn from
BED_GAIN = 0.55                # calibrated against the published clip's RMS
                               # profile (0.45 rendered ~2 dB too quiet)
BED_DIP = 0.5                  # extra dip under the pitch card
FADE_OUT = 1.5                 # seconds of fade at the very end

VIDEO_ARGS = ["-c:v", "libx264", "-preset", "medium", "-crf", "18",
              "-pix_fmt", "yuv420p", "-r", str(FPS)]
AUDIO_ARGS = ["-c:a", "aac", "-b:a", "160k", "-ar", "48000"]


# --------------------------------------------------------------------------
# Small subprocess helpers
# --------------------------------------------------------------------------

def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True)
    return json.loads(out.stdout)


def pan_crop() -> str:
    """The panning vertical crop, shared by both passes. `t` is seconds
    since the start of the moment (the trim below resets timestamps)."""
    return f"crop={CROP_W}:{CROP_H}:x='{PAN_X0}+{PAN_V}*t':y={PICTURE_Y}"


def moment_chain() -> list[str]:
    """The filter prefix both passes share: cut the moment out of the
    trailer and frame it vertically. One definition, so the hook and the
    replay are framed identically, frame for frame, by construction."""
    return [f"trim=end={HOOK_DUR}", "setpts=PTS-STARTPTS", pan_crop()]


def drawtext(text: str, size: int, y: int, colour: str = "white",
             border: int = 3, enable: str | None = None) -> str:
    f = (f"drawtext=fontfile={FONT}:text='{text}':fontsize={size}:"
         f"fontcolor={colour}:borderw={border}:bordercolor=black:"
         f"x=(w-text_w)/2:y={y}")
    if enable:
        f += f":enable='{enable}'"
    return f


def pitch_filters(prefix: str) -> list[str]:
    """The two-stage pitch card, drawn on the replay pass. Times are local
    to the replay segment."""
    t1, t2 = PITCH_START, PITCH_START + PITCH_URL_DELAY
    return [
        f"drawbox=x={BOX_X}:y={BOX_Y}:w={BOX_W}:h={BOX_H1}:"
        f"color=black@0.45:t=fill:enable='gte(t,{t1})'",
        f"drawbox=x={BOX_X}:y={BOX_Y + BOX_H1}:w={BOX_W}:h={BOX_H2 - BOX_H1}:"
        f"color=black@0.45:t=fill:enable='gte(t,{t2})'",
        drawtext(PITCH_LINES[0], 58, 688, border=2, enable=f"gte(t,{t1})"),
        drawtext(PITCH_LINES[1], 58, 783, border=2, enable=f"gte(t,{t1})"),
        drawtext(PITCH_URL, 54, 903, colour="yellow", border=2,
                 enable=f"gte(t,{t2})"),
    ]


# --------------------------------------------------------------------------
# Segment builders
# --------------------------------------------------------------------------

def render_hook(dest: Path) -> None:
    """The moment at full speed with the hook caption (video only)."""
    vf = ",".join([
        *moment_chain(),
        f"scale={OUT_W}:{OUT_H}:flags=lanczos",
        drawtext(HOOK_TEXT, 78, CAPTION_Y, border=4),
        "format=yuv420p",
    ])
    run(["ffmpeg", "-y", "-v", "error", "-ss", MOMENT_START, "-i", SOURCE,
         "-vf", vf, "-frames:v", HOOK_FRAMES, "-an", *VIDEO_ARGS, dest])


def render_replay(dest: Path) -> None:
    """The moment in smooth slow motion (video only).

    The 56 source frames are motion-interpolated up to 901 frames at the
    small crop size (cheap, and the upscale hides interpolation softness),
    then the timestamps are stretched so the pass lasts 30.03 s.
    """
    slow = REPLAY_FRAMES / HOOK_FRAMES              # 16.0893
    interp_fps = FPS * slow                          # 482.68
    filters = [
        *moment_chain(),
        f"minterpolate=fps={interp_fps:.2f}:mi_mode=mci:mc_mode=aobmc:"
        f"me_mode=bidir:vsbmc=1",
        f"setpts={slow:.4f}*PTS",
        f"scale={OUT_W}:{OUT_H}:flags=lanczos",
        drawtext(TAG_TEXT, 64, CAPTION_Y, border=4,
                 enable=f"lt(t,{TAG_DUR})"),
        *pitch_filters("replay"),
        "format=yuv420p",
    ]
    run(["ffmpeg", "-y", "-v", "error", "-ss", MOMENT_START, "-i", SOURCE,
         "-vf", ",".join(filters), "-frames:v", REPLAY_FRAMES, "-an",
         *VIDEO_ARGS, dest])


def render_audio(dest: Path) -> None:
    """Hook audio is the moment's own; the replay rides the trailer's
    climax bed, dipped under the pitch and faded out at the end."""
    hook = (f"[0:a]atrim=start={MOMENT_START}:end={MOMENT_START + HOOK_DUR},"
            f"asetpts=PTS-STARTPTS[hook]")
    bed = (f"[0:a]atrim=start={BED_START}:end={BED_START + REPLAY_DUR},"
           f"asetpts=PTS-STARTPTS,"
           f"volume={BED_GAIN},"
           f"volume='if(gte(t,{PITCH_START}),{BED_DIP},1)':eval=frame[bed]")
    fade_start = TOTAL_DUR - FADE_OUT
    graph = ";".join([
        hook, bed,
        f"[hook][bed]concat=n=2:v=0:a=1,"
        f"afade=t=out:st={fade_start:.2f}:d={FADE_OUT},"
        f"atrim=end={TOTAL_DUR}[out]",
    ])
    run(["ffmpeg", "-y", "-v", "error", "-i", SOURCE,
         "-filter_complex", graph, "-map", "[out]", *AUDIO_ARGS, dest])


def mux(hook: Path, replay: Path, audio: Path, dest: Path) -> None:
    """Join the two video segments and lay the audio under them. Both
    segments share identical encoding parameters, so the video can be
    joined with the concat demuxer and stream-copied — no third encode."""
    listing = hook.parent / "concat.txt"
    listing.write_text(f"file '{hook.resolve()}'\nfile '{replay.resolve()}'\n")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", listing, "-i", audio, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", *AUDIO_ARGS, "-movflags", "+faststart", dest])


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------

def verify(path: Path) -> bool:
    info = probe(path)
    dur = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    fps = eval(v["avg_frame_rate"])  # avg_frame_rate is a fraction string
    print(f"\n{path.name}: duration={dur:.2f}s "
          f"video={v['codec_name']} {v['width']}x{v['height']} @{fps:.0f}fps "
          f"audio={a['codec_name'] if a else 'NONE'}")
    ok = (abs(dur - TOTAL_DUR) <= 0.15 and v["width"] == OUT_W
          and v["height"] == OUT_H and a is not None)
    print("shape check:", "OK" if ok else "MISMATCH vs the published clip")
    return ok


def grab_frames(path: Path, build: Path) -> None:
    for t, name in [(0.9, "check_hook"), (3.0, "check_tag"),
                    (12.0, "check_mid"), (28.0, "check_pitch")]:
        run(["ffmpeg", "-y", "-v", "error", "-ss", t, "-i", path,
             "-frames:v", "1", build / f"{name}.jpg"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=WORK / "clip_rendered.mp4")
    ap.add_argument("--keep", action="store_true",
                    help="keep the intermediate segment files")
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"{tool} not found", file=sys.stderr)
            return 1
    if not SOURCE.exists():
        print(f"source trailer missing: {SOURCE}", file=sys.stderr)
        return 1

    build = WORK / "render_build"
    build.mkdir(exist_ok=True)
    hook, replay, audio = (build / "seg_hook.mp4", build / "seg_replay.mp4",
                           build / "audio.m4a")

    render_hook(hook)
    render_replay(replay)
    render_audio(audio)
    mux(hook, replay, audio, args.out)
    ok = verify(args.out)
    grab_frames(args.out, build)
    print(f"check frames are in {build}/ (check_hook/tag/mid/pitch.jpg)")

    if not args.keep:
        for f in (hook, replay, audio):
            f.unlink(missing_ok=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
