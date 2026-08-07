from setuptools import setup, find_packages

setup(
    name="agent-qa-guard",
    version="1.0.0",
    author="Autonomous Circularity Network (ACN)",
    author_email="dev@acn-network.org",
    description="CI/CD Linter & Secret Scanner for AI Agent Codebases & Tool Trajectories",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ivegotahunnitonit/acn-security-action",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "agent-qa=agent_qa_guard.cli:main",
        ],
    },
)
