# Hermes Deepgram Voice Plugin

Standalone [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin for:

- **Deepgram Aura 2 TTS** via `POST /v1/speak`
- **Deepgram Nova STT** via `POST /v1/listen`
- Native MP3, OGG/Opus, WAV, and FLAC output
- Automatic spoken-language detection by default
- Hermes setup/picker metadata and dotenv-aware credentials
- No Deepgram SDK dependency; the plugin uses the documented REST APIs

This is the standalone-plugin implementation requested by [NousResearch/hermes-agent#10703](https://github.com/NousResearch/hermes-agent/issues/10703). It adapts the previous in-tree Deepgram work to Hermes' `TTSProvider` and `TranscriptionProvider` plugin interfaces.

## Install

```bash
hermes plugins install jaysonsantos/hermes-deepgram-voice-plugin --enable
```

The installer prompts for `DEEPGRAM_API_KEY` and stores it in `~/.hermes/.env`. Restart Hermes after installation.

Alternatively, install the Python package into the same Python environment as Hermes. The `hermes_agent.plugins` entry point is discovered automatically:

```bash
pip install git+https://github.com/jaysonsantos/hermes-deepgram-voice-plugin.git
```

## Configure TTS

```yaml
# ~/.hermes/config.yaml
tts:
  provider: deepgram
  voice: aura-2-thalia-en
  output_format: mp3       # mp3 | ogg | opus | wav | flac
  speed: 1.0
  deepgram:
    timeout: 60
    # base_url: https://api.deepgram.com/v1
    # encoding: mp3
    # container: none
    # sample_rate: 24000
    # bit_rate: 48000
```

Aura voice IDs are sent through Deepgram's `model` query parameter. `tts.voice` is therefore the primary voice selector. The default is `aura-2-thalia-en`.

## Configure STT

```yaml
stt:
  enabled: true
  provider: deepgram
  deepgram:
    model: nova-3
    language: ""            # empty = auto-detect
    detect_language: true
    smart_format: true
    punctuate: true
    diarize: false
    paragraphs: false
    utterances: false
    numerals: false
    dictation: false
    timeout: 120
    # base_url: https://api.deepgram.com/v1
```

When `language` is empty, the plugin sends `detect_language=true`. Set `language` to a BCP-47/language code such as `en`, `de`, or `pt-BR` only when you want to force it.

## Environment overrides

| Variable | Purpose |
|---|---|
| `DEEPGRAM_API_KEY` | Required API credential |
| `DEEPGRAM_TTS_BASE_URL` | Optional TTS proxy/custom endpoint |
| `DEEPGRAM_STT_BASE_URL` | Optional STT proxy/custom endpoint |

Hermes' dotenv-aware `get_env_value()` is used, so values in `~/.hermes/.env` work without exporting them in the shell.

## Compatibility

The plugin requires a Hermes version with `PluginContext.register_tts_provider()` (and, for STT, `register_transcription_provider()`). If the STT hook is unavailable, TTS still registers. If your local Hermes branch already carries Deepgram as a built-in STT provider, the built-in wins by design; the plugin still provides TTS.

## Development

Requirements: [uv](https://docs.astral.sh/uv/) and Python 3.11–3.13.

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
PYTHONPATH=$HOME/.hermes/hermes-agent uv run pytest
uv run pre-commit run --all-files
uv build
```

The test suite mocks Deepgram HTTP calls; no API key or paid request is needed.

## Credits

The REST behavior and test cases build on the earlier in-tree work in Hermes PRs [#10734](https://github.com/NousResearch/hermes-agent/pull/10734) and [#27506](https://github.com/NousResearch/hermes-agent/pull/27506), plus Jayson's local Deepgram STT branch.

## License

MIT
