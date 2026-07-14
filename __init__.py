"""Directory-plugin entry point for Hermes Agent."""

try:
    from .hermes_deepgram_voice import register
except ImportError:  # Loaded directly by test/build tooling rather than Hermes.
    from hermes_deepgram_voice import register

__all__ = ["register"]
