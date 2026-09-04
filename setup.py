from setuptools import setup

setup(
    name="btp-guard",
    version="2.5.0",
    description="Frontier MCP Security Proxy, Sub-Microsecond OS Event Gating, Copy-on-Write Rollback Engine & In-Flight Secret Scrubber for Autonomous AI Agents.",
    author="Bartholomew Protocol Team",
    packages=["btp_guard"],
    package_dir={"btp_guard": "src"},
    python_requires=">=3.10",
    install_requires=[
        "cryptography>=41.0.0",
        "pyyaml>=6.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "pydantic>=2.0.0",
        "requests>=2.28.0"
    ],
    entry_points={
        "console_scripts": [
            "bartholomew=btp_guard.cli:main",
            "btp=btp_guard.cli:main",
            "btp-mcp=btp_guard.mcp_gateway:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography"
    ]
)
