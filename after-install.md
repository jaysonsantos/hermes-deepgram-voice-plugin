# Deepgram Voice installed

Set one or both providers in `~/.hermes/config.yaml`:

```yaml
tts:
  provider: deepgram
  voice: aura-2-thalia-en
  output_format: mp3

stt:
  provider: deepgram
  deepgram:
    model: nova-3
    detect_language: true
```

Then restart Hermes. See the repository README for all options.
