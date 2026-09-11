from setuptools import setup

setup(
    name="btp-guard",
    version="5.4.5",
    description="Bartholomew Protocol (BTP v5.4.5) -- Sovereign Sentinel Companion & Autonomous AI Agent Execution Gateway. Sub-35us AST safety gating, in-flight secret scrubbing, and multi-model defense for GPT-Astra, Claude 3.7, Gemini 2.0, DeepSeek-R1, CrewAI, LangGraph, AutoGen, and LlamaIndex.",
    author="Bartholomew Protocol Team",
    packages=[
        "btp_guard",
        "framework_adapters",
        "framework_adapters.crewai",
        "framework_adapters.langgraph",
        "framework_adapters.autogen",
        "framework_adapters.llamaindex",
        "framework_adapters.universal"
    ],
    package_dir={"btp_guard": "src"},
    python_requires=">=3.10",
    install_requires=[
        "cryptography>=41.0.0",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "requests>=2.28.0"
    ],
    entry_points={
        "console_scripts": [
            "bartholomew=cli:main",
            "btp=cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography"
    ]
)
