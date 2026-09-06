"""
Bartholomew Trust Protocol (BTP v5.4) — High-Performance Audio Codec
Pure Python, zero-dependency ITU-T G.711 mu-law encoder/decoder and resampler.
Fully compatible with Python 3.14+ (no deprecated audioop dependency).
"""

import base64
import math
import struct
from typing import Tuple


# ITU-T G.711 mu-law Lookup Tables
BIAS = 0x84
CLIP = 32635

# Precompute 256-byte mu-law decode table (8-bit mu-law -> 16-bit linear PCM)
_MULAW_DECODE_TABLE = [0] * 256
for _i in range(256):
    _val = ~_i
    _sign = _val & 0x80
    _exponent = (_val >> 4) & 0x07
    _mantissa = _val & 0x0F
    _sample = ((_mantissa << 3) + BIAS) << _exponent
    _sample -= BIAS
    _MULAW_DECODE_TABLE[_i] = -_sample if _sign != 0 else _sample

# Precompute 16-bit linear PCM to 8-bit mu-law encode table
# Map 65536 signed 16-bit values to 256 mu-law codes
_MULAW_ENCODE_TABLE = bytearray(65536)
for _pcm in range(-32768, 32768):
    _sign = 0x80 if _pcm < 0 else 0
    _mag = -_pcm if _pcm < 0 else _pcm
    if _mag > CLIP:
        _mag = CLIP
    _mag += BIAS

    # Find exponent
    _exp = 7
    for _e, _bound in enumerate((0xFF, 0x1FF, 0x3FF, 0x7FF, 0xFFF, 0x1FFF, 0x3FFF, 0x7FFF)):
        if _mag <= _bound:
            _exp = _e
            break

    _mantissa = (_mag >> (_exp + 3)) & 0x0F
    _mulaw_byte = ~(_sign | (_exp << 4) | _mantissa) & 0xFF
    # Map signed 16-bit (-32768..32767) into array index (0..65535)
    _idx = (_pcm + 32768) & 0xFFFF
    _MULAW_ENCODE_TABLE[_idx] = _mulaw_byte


class AudioCodec:
    """Zero-dependency audio transcoder for Twilio telephony and OpenAI Realtime."""

    @staticmethod
    def mulaw_to_pcm16(mulaw_bytes: bytes) -> bytes:
        """
        Convert ITU-T G.711 mu-law (8kHz 8-bit) to linear PCM16 (8kHz 16-bit signed, little-endian).
        """
        samples = [_MULAW_DECODE_TABLE[b] for b in mulaw_bytes]
        return struct.pack(f"<{len(samples)}h", *samples)

    @staticmethod
    def pcm16_to_mulaw(pcm16_bytes: bytes) -> bytes:
        """
        Convert linear PCM16 (8kHz 16-bit signed, little-endian) to ITU-T G.711 mu-law (8kHz 8-bit).
        """
        num_samples = len(pcm16_bytes) // 2
        if num_samples == 0:
            return b""
        samples = struct.unpack(f"<{num_samples}h", pcm16_bytes)
        result = bytearray(num_samples)
        for i, s in enumerate(samples):
            idx = (s + 32768) & 0xFFFF
            result[i] = _MULAW_ENCODE_TABLE[idx]
        return bytes(result)

    @staticmethod
    def resample_8k_to_24k(pcm16_8k: bytes) -> bytes:
        """
        Upsample linear PCM16 from 8,000 Hz to 24,000 Hz (3x upsampling with linear interpolation).
        """
        num_samples = len(pcm16_8k) // 2
        if num_samples == 0:
            return b""
        samples_8k = struct.unpack(f"<{num_samples}h", pcm16_8k)
        
        # 3x linear interpolation
        samples_24k = []
        for i in range(num_samples - 1):
            s0 = samples_8k[i]
            s1 = samples_8k[i + 1]
            samples_24k.append(s0)
            samples_24k.append(int(s0 + (s1 - s0) * (1 / 3)))
            samples_24k.append(int(s0 + (s1 - s0) * (2 / 3)))
        
        # Last sample
        last = samples_8k[-1]
        samples_24k.extend([last, last, last])
        
        return struct.pack(f"<{len(samples_24k)}h", *samples_24k)

    @staticmethod
    def resample_24k_to_8k(pcm16_24k: bytes) -> bytes:
        """
        Downsample linear PCM16 from 24,000 Hz to 8,000 Hz (3:1 decimation with 3-sample averaging).
        """
        num_samples = len(pcm16_24k) // 2
        if num_samples < 3:
            return b""
        samples_24k = struct.unpack(f"<{num_samples}h", pcm16_24k)
        
        # Take mean of every 3 samples to avoid aliasing
        num_8k = num_samples // 3
        samples_8k = [
            int((samples_24k[i * 3] + samples_24k[i * 3 + 1] + samples_24k[i * 3 + 2]) / 3)
            for i in range(num_8k)
        ]
        return struct.pack(f"<{len(samples_8k)}h", *samples_8k)

    @staticmethod
    def twilio_to_openai(twilio_mulaw_b64: str) -> str:
        """
        Full inbound pipeline:
        Twilio Base64 (8kHz mu-law) -> PCM16 8kHz -> PCM16 24kHz -> Base64 for OpenAI Realtime API.
        """
        raw_mulaw = base64.b64decode(twilio_mulaw_b64)
        pcm16_8k = AudioCodec.mulaw_to_pcm16(raw_mulaw)
        pcm16_24k = AudioCodec.resample_8k_to_24k(pcm16_8k)
        return base64.b64encode(pcm16_24k).decode("ascii")

    @staticmethod
    def openai_to_twilio(openai_pcm24k_b64: str) -> str:
        """
        Full outbound pipeline:
        OpenAI Realtime Base64 (24kHz PCM16) -> PCM16 8kHz -> 8kHz mu-law -> Base64 for Twilio MediaStream.
        """
        pcm16_24k = base64.b64decode(openai_pcm24k_b64)
        pcm16_8k = AudioCodec.resample_24k_to_8k(pcm16_24k)
        mulaw = AudioCodec.pcm16_to_mulaw(pcm16_8k)
        return base64.b64encode(mulaw).decode("ascii")

    @staticmethod
    def calculate_rms(pcm16_bytes: bytes) -> float:
        """Calculate Root Mean Square (RMS) energy for voice activity detection."""
        num_samples = len(pcm16_bytes) // 2
        if num_samples == 0:
            return 0.0
        samples = struct.unpack(f"<{num_samples}h", pcm16_bytes)
        sum_squares = sum(s * s for s in samples)
        return math.sqrt(sum_squares / num_samples)
