// gta6-clipper-01 entry program (Node, standard library only).
//
// The entry is the video: VIDEO.json, at this repository's root, names the
// public YouTube Short — "A plane just buzzed Jason's motorcycle in GTA 6"
// (https://youtube.com/shorts/NIOfFrRmwEU). The clip itself was cut from
// GTA 6 Trailer 2 by render.py; see README.md for the moment and the cut.
//
// All this program has to do is hand VIDEO.json to the grader: copy it from
// the bot directory into the output directory, where the gate reads it.
// Nothing it writes about the video is scored — places go by the video's
// views, which the house reads from YouTube itself.
//
// In the grader's container the directories are /bot and /output; outside
// it, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR stand in for them:
//
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
//
// On success it prints nothing. If VIDEO.json cannot be copied it says why
// on stderr and exits 1.

import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { join } from "node:path";

const VIDEO_FILE = "VIDEO.json";

function directoryFromEnv(name: string, fallback: string): string {
  const value = process.env[name];
  return value === undefined || value === "" ? fallback : value;
}

function main(): void {
  const botDir = directoryFromEnv("MAKEFUN_BOT_DIR", "/bot");
  const outputDir = directoryFromEnv("MAKEFUN_OUTPUT_DIR", "/output");
  const source = join(botDir, VIDEO_FILE);
  const destination = join(outputDir, VIDEO_FILE);

  mkdirSync(outputDir, { recursive: true });
  copyFileSync(source, destination);

  // Fail loudly rather than hand the gate a truncated file: the copy must
  // have landed at exactly the source's size.
  const copied = statSync(destination).size;
  const expected = statSync(source).size;
  if (copied !== expected) {
    throw new Error(
      `incomplete copy: ${destination} is ${copied} bytes, expected ${expected}`,
    );
  }
}

try {
  main();
} catch (err) {
  console.error(`could not deliver ${VIDEO_FILE}: ${(err as Error).message}`);
  process.exit(1);
}
