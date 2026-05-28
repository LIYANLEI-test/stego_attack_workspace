# Repository Instructions

Start every new task by reading:

1. `.planning/STATE.md`
2. `.planning/PROJECT.md`
3. The relevant method doc under `docs/`

Use GSD planning state for future work. If `gsd-sdk` is unavailable, keep `.planning/` updated manually and document the tooling issue in `.planning/STATE.md`.

The baseline rule is native original-repository generation/recovery whenever practical. Local compatibility adaptations may handle paths, caches, checkpoint links, imports, logging, or runner plumbing, but they must not change embedding, sampling, inversion, decoding, ECC, payload mapping, or metric semantics unless the result is explicitly labeled as a non-paper variant.

Large models, generated images, run CSVs, and logs stay under `/data2/liyanlei/...`. GitHub should track scripts, configs, docs, small manifests, summaries, and planning state.

Keep provenance labels honest:

- CRoSS, Pulsar, GSD, MAS/GRDH, and RGS are `native_official`.
- MDDM is `native_third_party` until an official implementation is integrated.
- Diffusion-Stego has been removed from the active project because only a
  projection-only NS-DSer reference path was available; do not re-add it without
  a full image-generation/reveal implementation.

After meaningful task updates, commit and push to `origin/main` unless the user asks for a separate branch.
