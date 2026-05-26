---
status: complete
created: 2026-05-27
completed: 2026-05-27T00:00:00+08:00
---

# Summary

Checked `and-mill/semantic-forgery` at commit
`ca68950cd7b53b8438a49580f134b2a0db28d778`.

Decision: do not include it as a current hidden-payload destruction baseline.
It attacks Tree-Ring/Gaussian-Shading semantic watermarks and relies on those
watermark providers/verifiers. The native scripts do not match our current
quality-budget protocol of applying a generic, content-preserving image-domain
attack to arbitrary stego artifacts before each method's native reveal.

No 10-image smoke was run because doing so would test a different task rather
than our generative steganography recovery setting.

Doc:

```text
docs/semantic_forgery_suitability_20260527.md
```
