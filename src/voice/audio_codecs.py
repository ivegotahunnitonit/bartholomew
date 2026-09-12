"""
Bartholomew Voice AI — Audio Codec, Resampling & Tone Detection Utilities
High-performance, zero-dependency audio conversion between Twilio (G.711 mu-law 8kHz)
and Gemini Live (16-bit linear PCM at 16kHz / 24kHz), plus Goertzel voicemail beep tone detection.
"""

import struct
import math
from typing import Tuple, List

# ---------------------------------------------------------------------------
# G.711 mu-law Decoding Table (8-bit mu-law -> 16-bit signed integer)
# ---------------------------------------------------------------------------
MULAW_TO_LINEAR = [0] * 256
for _i in range(256):
    _inv = ~_i & 0xFF
    _sign = -1 if (_inv & 0x80) else 1
    _exponent = (_inv >> 4) & 0x07
    _mantissa = _inv & 0x0F
    _sample = _sign * ((_mantissa << 3) + 132) << _exponent
    _sample -= _sign * 132
    MULAW_TO_LINEAR[_i] = max(-32768, min(32767, _sample))


def mulaw8k_to_pcm16k(mulaw_bytes: bytes) -> bytes:
    """
    Converts 8kHz 8-bit mu-law audio (from Twilio) to 16kHz 16-bit linear PCM (for Gemini).
    Performs 2:1 linear interpolation upsampling.
    """
    if not mulaw_bytes:
        return b""
    
    # Decode 8kHz samples
    pcm8k = [MULAW_TO_LINEAR[b] for b in mulaw_bytes]
    n = len(pcm8k)
    
    # 2x linear interpolation upsampling
    pcm16k = []
    for i in range(n - 1):
        s0 = pcm8k[i]
        s1 = pcm8k[i + 1]
        pcm16k.append(s0)
        pcm16k.append((s0 + s1) // 2)
    # Append the last sample duplicated
    if n > 0:
        pcm16k.append(pcm8k[-1])
        pcm16k.append(pcm8k[-1])
        
    return struct.pack(f"<{len(pcm16k)}h", *pcm16k)


def pcm24k_to_mulaw8k(pcm24k_bytes: bytes) -> bytes:
    """
    Converts 24kHz 16-bit linear PCM audio (from Gemini Live) to 8kHz 8-bit mu-law (for Twilio).
    Performs 3:1 downsampling and G.711 mu-law compression.
    """
    if not pcm24k_bytes:
        return b""
        
    num_samples = len(pcm24k_bytes) // 2
    if num_samples == 0:
        return b""
        
    samples = struct.unpack(f"<{num_samples}h", pcm24k_bytes[:num_samples * 2])
    
    out = bytearray()
    # 3:1 downsampling: take 1 out of every 3 samples
    for i in range(0, num_samples, 3):
        sample = samples[i]
        sign = 0x80 if sample < 0 else 0
        if sample < 0:
            sample = -sample
        sample += 132
        if sample > 32767:
            sample = 32767
            
        exponent = 7
        for exp_idx in range(7):
            if sample < (1 << (exp_idx + 7)):
                exponent = exp_idx
                break
                
        mantissa = (sample >> (exponent + 3)) & 0x0F
        mulaw_byte = ~(sign | (exponent << 4) | mantissa) & 0xFF
        out.append(mulaw_byte)
        
    return bytes(out)


# ---------------------------------------------------------------------------
# Goertzel Algorithm for Voicemail Beep Tone Detection
# ---------------------------------------------------------------------------

def detect_tone_goertzel(
    pcm16_samples: List[int],
    target_freq: float = 1000.0,
    sample_rate: float = 8000.0
) -> float:
    """
    Computes normalized relative spectral power at target frequency using Goertzel algorithm.
    Returns relative energy ratio between 0.0 and 1.0.
    """
    n = len(pcm16_samples)
    if n < 8:
        return 0.0

    k = int(0.5 + (n * target_freq / sample_rate))
    omega = (2.0 * math.pi * k) / n
    coeff = 2.0 * math.cos(omega)

    s_prev = 0.0
    s_prev2 = 0.0
    total_energy = 0.0

    for sample in pcm16_samples:
        total_energy += sample * sample
        s = sample + (coeff * s_prev) - s_prev2
        s_prev2 = s_prev
        s_prev = s

    power = (s_prev * s_prev) + (s_prev2 * s_prev2) - (coeff * s_prev * s_prev2)
    if total_energy <= 0.0:
        return 0.0

    normalized_power = power / (n * total_energy)
    return min(1.0, max(0.0, normalized_power))


def detect_voicemail_beep(
    pcm16_bytes: bytes,
    target_freq: float = 1000.0,
    sample_rate: float = 8000.0,
    confidence_threshold: float = 0.35,
    min_rms: float = 1200.0
) -> Tuple[bool, float]:
    """
    Evaluates whether an audio chunk contains a voicemail beep tone.
    Checks both RMS volume and Goertzel spectral concentration around 1000 Hz.
    """
    if not pcm16_bytes or len(pcm16_bytes) < 16:
        return False, 0.0

    num_samples = len(pcm16_bytes) // 2
    samples = struct.unpack(f"<{num_samples}h", pcm16_bytes[:num_samples * 2])

    # RMS calculation
    sum_sq = sum(s * s for s in samples)
    rms = math.sqrt(sum_sq / num_samples) if num_samples > 0 else 0.0

    if rms < min_rms:
        return False, 0.0

    score = detect_tone_goertzel(list(samples), target_freq=target_freq, sample_rate=sample_rate)
    is_beep = score >= confidence_threshold
    return is_beep, score
