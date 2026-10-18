# Native camera paths: evidence and writer decision

## CONFIRMED IN MANUAL/SDK

`research/sdk/cutscene.htm.txt`: one key is a static camera, multiple keys play in order, `PlayPath(client, script, filename, rate)` uses a rate (example 30), not a duration in seconds. The original debug camera could add/insert/delete/save keys. RCM does not invoke those tools.

## CONFIRMED IN ORIGINAL FILE

`ncp_catalogue.json` inventories all 174 NCPs in Resource.nob with SHA-256 and every float. Header: uint32 key count, float32 final path parameter. Then count × 104 bytes. All values are little-endian. Single-key originals can contain enormous unused polynomial coefficients: preserve them on roundtrip rather than sanitising original bytes. No magic, version or checksum is present in the original reader.

## CONFIRMED IN NATIVE READER / WRITER / EVALUATOR

`native_ncp.txt` is generated from the current installation's Vampire.exe; its hash is in `source_identity.json`.

- Console save wrapper `0x4079d0` calls `0x431530`. It writes count, final parameter and 104-byte records verbatim.
- Console load wrapper `0x4079f0` calls `0x431600`. It accepts **1..128** keys and reads those exact fields. The native buffer has 128 records. This is the authoring limit, not an arbitrary UI cap.
- `0x430350` advances a path parameter by frame delta × playback speed and compares it with the header parameter. At the end it uses the final key's position/orientation.
- `0x430479..0x4304bd` finds a segment and computes `u=(parameter-key.parameter)*key.inverse_span`.
- `0x4304ea..0x43069a` evaluates independent cubic polynomials for position and Euler angles: `base + linear*u + quadratic*u² + cubic*u³`.
- Per record: offsets 0 parameter, 4 inverse span, 8 position base[3], 20 position linear[3], 32 position quadratic[3], 44 position cubic[3], 56 Euler base[3], 68 Euler linear[3], 80 Euler quadratic[3], 92 Euler cubic[3]. Every byte is accounted for by the evaluator. Euler angles are converted using the native degree-to-radian helper before constructing the camera matrix.
- `0x431110` computes segment lengths from neighbouring positions, sets inverse span and computes cubic coefficients. RCM need not duplicate its smoothing algorithm to write a valid polynomial path.
- Java PlayPath wrapper `0x46e1a0` supplies a separate fixed camera lens argument to `0x430e60`. **No FOV field exists in the NCP record.** RCM does not expose a fictitious FOV key.

## WRITER DECISION

Write a conservative **linear polynomial subset**: position/Euler bases and deltas, zero quadratic/cubic coefficients, cumulative position distance as parameter and reciprocal segment distance. The last key has zero coefficients and reciprocal span. This follows the demonstrated evaluator rather than copying uninitialised coefficients from originals. Consecutive coincident positions in a moving path are rejected; a static path is one key. Rotation takes the shortest angular delta. This interpolation differs deliberately from the original debug tool's cubic smoothing and is described as linear in the editor.

The reader preserves every raw float for exact original roundtrip, including unused single-key data. New authored data rejects non-finite values, excessive coordinates/counts, zero-length segments and inconsistent parameter progression. No original file is modified.

## REQUIRES NATIVE TEST

Visual position/orientation from viewport capture, linear interpolation, speed, endpoint hold, collision and lifecycle on save/abort need EMB08–17. Binary evidence and mathematical tests do not count as rendered acceptance.
