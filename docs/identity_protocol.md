# Identity Experiment Protocol

This workspace uses one deterministic protocol for identity runs before attack
experiments.

## Scope

Bit-payload methods use `500` samples.

Image-payload methods, currently CRoSS and RGS, use the fixed `100` FFHQ secret
images:

```text
/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/images
```

The two groups are reported in separate tables because bit recovery and image
recovery have different metrics.

## Unified Message Seed

All bit-payload messages are derived from one protocol seed:

```text
stego-attack-native-identity-v1-20260522
```

Payload length is method-specific, following each method's native capacity or
native payload shape. This avoids forcing high-capacity methods to carry an
artificially short message.

Examples:

```text
Pulsar: dynamic bytes, equal to estimate_regions() capacity for that sample
MDDM: 2048 printable ASCII bytes for the SD1.5 latent text interface
MAS/GRDH: 16384 bits for 4*64*64 SD latent payload
GSD CIFAR-10: 3072 bits for 3*32*32 DDPM payload
GSD CelebA-64: 12288 bits for 3*64*64 DDPM payload
```

Within each method, every sample uses a deterministic message generated from:

```text
SHAKE256(protocol_seed | method | sample_index | payload_length)
```

For text-only interfaces, random bytes are mapped to printable ASCII. Every
result row records the exact payload length used.

Generated protocol files:

```text
/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522/manifest.json
/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522/method_payload_specs.json
/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522/prompts_500.txt
/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522/image_payloads_100.csv
```

## Payload And Paper Semantics

The protocol keeps each method's native payload shape:

```text
Pulsar uses the per-sample Sage/region capacity estimated by the official path.
GSD uses the DCT sign tensor shape used by sample_reverse_dct.
MAS/GRDH uses the 1-bit-per-latent-element message used by the official mapping module.
CRoSS and RGS use full secret images instead of bit strings.
```

The runners replace random payload generation with deterministic protocol
payloads so results are comparable and resumable. They should not change
embedding, sampling, inversion, decoding, ECC, or metric semantics. If a method
does not have an integrated official repository, the result label must say so;
currently that applies to MDDM (`native_third_party`).
