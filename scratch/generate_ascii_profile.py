"""
Convert founder_avatar.jpg to ASCII code art and generate a high-tech terminal GitHub profile README.
"""

from PIL import Image
import os

def image_to_ascii(image_path, width=42, height_ratio=0.52):
    img = Image.open(image_path)
    # Convert to grayscale
    img = img.convert('L')
    
    orig_w, orig_h = img.size
    aspect_ratio = orig_h / orig_w
    target_h = int(width * aspect_ratio * height_ratio)
    
    img = img.resize((width, target_h), Image.Resampling.LANCZOS)
    
    # High-tech code character density ramp (dark to light)
    chars = " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya2ESwqkP6h9d4VpOGbUAKXHm8&%$#@MWB"
    
    pixels = img.getdata()
    ascii_lines = []
    
    for y in range(target_h):
        line = ""
        for x in range(width):
            idx = y * width + x
            pixel_val = pixels[idx]
            # Map pixel value 0-255 to char index
            char_idx = int((pixel_val / 255) * (len(chars) - 1))
            line += chars[char_idx]
        ascii_lines.append(line)
        
    return ascii_lines

def build_profile_readme(ascii_lines):
    # Right side specs
    specs = [
        "bartholomew@core-engine ----------------------------------------------------",
        " OS: ....................................... Windows 11, Linux (Ubuntu/Debian)",
        " Role: ................................. Lead Architect & Systems Engineer",
        " Platform: ............................. Bartholomew Autonomous Systems",
        " Kernel: ............................... Mechanical AST Verifier (BTP v0.1)",
        " Latency: .............................. 1.14 µs (11.98M ops/sec Go Daemon)",
        " IDE: .................................. Antigravity IDE, VS Code, JetBrains",
        " ",
        " Languages.Core: ....................... Python 3.14, Go 1.23, Rust, C++",
        " Languages.Systems: .................... AST Grammars, POSIX Kernel, Linux eBPF",
        " Cryptography: ......................... RFC 8785 JCS, Ed25519, SHA-256",
        " Cloud.Infra: .......................... Google Cloud Run, Firebase, Docker",
        " ",
        " Focus.Engineering: .................... Deterministic CI/CD Auto-Remediation",
        " Focus.Security: ....................... Zero-Trust Agent Trajectory Firewalls",
        " Focus.Verification: ................... 100% Pre-Flight Test Suite Guarantees",
        " ",
        " - Contact ----------------------------------------------------------------",
        "  Email.Support: ..................................... help@bartholomew.info",
        "  Email.Inbound: .................................... itsub@bartholomew.info",
        "  Platform.Live: ................................. https://www.bartholomew.info",
        "  Dashboard.App: ................................. https://app.bartholomew.info",
        " ",
        " - Empirical Benchmark Stats ----------------------------------------------",
        "  Verified Test Cycles: .......... 1,000,000 Cycles (100.0000% Pass Rate)",
        "  Failures / Regressions: ........ 0 (0.00000%) across 12 Parallel CPU Cores",
        "  Throughput: .................... 28,880 Cryptographic Operations / Sec",
        "  Average Surgical Delta: ........ 3 Lines AST Patch (Zero Drift / No Hallucinations)",
        " ---------------------------------------------------------------------------"
    ]
    
    # Combine side by side
    max_h = max(len(ascii_lines), len(specs))
    combined_lines = []
    
    for i in range(max_h):
        left = ascii_lines[i] if i < len(ascii_lines) else " " * len(ascii_lines[0])
        right = specs[i] if i < len(specs) else ""
        combined_lines.append(f"{left}   {right}")
        
    terminal_block = "\n".join(combined_lines)
    
    readme_content = f"""# **Bartholomew AI | Autonomous CI/CD Failure Auto-Fix**

<div align="center">

```text
{terminal_block}
```

[![Website](https://img.shields.io/badge/Live_Site-www.bartholomew.info-00f2fe?style=for-the-badge&logo=google-chrome&logoColor=040813)](https://www.bartholomew.info)
[![Dashboard](https://img.shields.io/badge/Command_Center-app.bartholomew.info-00e676?style=for-the-badge&logo=target&logoColor=040813)](https://app.bartholomew.info/dashboard)
[![Docs](https://img.shields.io/badge/Documentation-docs.bartholomew.info-4facfe?style=for-the-badge&logo=readme&logoColor=040813)](https://docs.bartholomew.info/docs)
[![License](https://img.shields.io/badge/License-Proprietary_Commercial-fbbf24?style=for-the-badge&logo=shield&logoColor=040813)](#intellectual-property--protective-license)

</div>

---

## 🔒 **Intellectual Property & Commercial Protection Notice**

> **NOTICE OF PROPRIETARY OWNERSHIP & RESTRICTED COMMERCIAL USE:**
> 
> All code, compiler AST transformations, Go trajectory intercept daemons, RFC 8785 cryptographic attestation algorithms, and autonomous reproduction pipelines contained within this repository are the exclusive proprietary intellectual property of **Bartholomew AI & Contributors**.
> 
> * **Zero Unauthorized Duplication:** No entity, organization, or automated crawler is granted permission to clone, sub-license, scrape, train commercial AI models upon, or re-distribute this codebase without an explicit, signed commercial licensing agreement.
> * **Cryptographic Verification:** Every commit, release artifact, and execution receipt is cryptographically hashed and signed via **RFC 8785 JSON Canonicalization and Ed25519 digital signatures** registered to our root key authority.
> * **Patent & Trade Secret Protections:** The mechanical AST delta synthesis, hermetic reproduction synthesis, and sub-microsecond POSIX execution boundary algorithms are protected under international copyright, trademark, and trade secret laws.

For commercial enterprise licensing, contact: **`help@bartholomew.info`**.

---

## ⚡ **Key Engineering Achievements**

* **1,000,000 Deterministic Cycles:** Tested across 12 parallel CPU cores with **100.0000% reliability (0 failures)**.
* **1.14 &mu;s Go Trajectory Daemon:** 11.98 million operations/second inline security firewall.
* **Compiler-Level AST Surgery:** Minimal 3-line patch delta leaving 100% of adjacent code untouched.
* **100% Pre-Flight Test Guarantee:** Zero PRs shipped unless all repository tests pass green.

---
© 2026 Bartholomew AI & Contributors. All Rights Reserved.
"""
    return readme_content

if __name__ == "__main__":
    avatar_path = "founder_avatar.jpg"
    if os.path.exists(avatar_path):
        lines = image_to_ascii(avatar_path, width=38, height_ratio=0.50)
        readme = build_profile_readme(lines)
        with open("PROFILE_README.md", "w", encoding="utf-8") as f:
            f.write(readme)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme)
        print("[SUCCESS] Generated ASCII Code Art Profile README to README.md and PROFILE_README.md")
    else:
        print(f"[ERROR] {avatar_path} not found!")
