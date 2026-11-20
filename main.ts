// news-image-20261119-final entry (Node 22, standard library only).
//
// The entry is a program that writes one image to /output/entry.png:
// the 1024x1024 infographic in entry.png beside this file, which sums
// up Thursday 19 November 2026 in six stories (the first-ever
// Trump-Xi-Putin trilateral summit, the ICJ genocide ruling against
// Myanmar, the third Kerch Bridge strike, Anthropic's record $81bn
// IPO, Cyclone Akvan's evacuation of 300,000 people, and Trump
// holding off on new Iran strikes until 2027), each checked against
// live reporting from that day. The image is drawn by
// generate_image.py in this repo; this program only validates and
// copies it, so the graded run is fully deterministic: no network,
// no clock, no randomness, and the same bytes every run.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";

const MAX_BYTES = 1_048_576;
const MAX_DIMENSION = 1024;
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function die(reason: string): never {
  throw new Error(`entry.png failed validation: ${reason}`);
}

function png_size(bytes: Buffer): { width: number; height: number } {
  if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) die("not a PNG file");
  // IHDR chunk: 8-byte signature, 4-byte length, 4-byte "IHDR",
  // then width and height as 4-byte big-endian integers.
  if (bytes.length < 33 || bytes.toString("ascii", 12, 16) !== "IHDR") {
    die("missing IHDR chunk");
  }
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

function main(): void {
  const source = new URL("./entry.png", import.meta.url);
  if (!existsSync(source)) die("entry.png is missing from the repository");
  if (!statSync(source).isFile()) die("entry.png is not a regular file");
  const bytes = readFileSync(source);
  if (bytes.length > MAX_BYTES) die(`too large: ${bytes.length} bytes`);
  const { width, height } = png_size(bytes);
  if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
    die(`too large: ${width}x${height} pixels`);
  }

  const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  mkdirSync(outputDir, { recursive: true });
  const output = join(outputDir, "entry.png");
  copyFileSync(source, output);

  // Prove the copy is byte-for-byte the source before finishing.
  const copied = readFileSync(output);
  const digest = (b: Buffer) => createHash("sha256").update(b).digest("hex");
  if (digest(copied) !== digest(bytes)) die("copied bytes differ from entry.png");

  console.log(
    `wrote ${output} (${width}x${height}, ${statSync(output).size} bytes, sha256 ${digest(copied).slice(0, 16)}...)`,
  );
}

main();
