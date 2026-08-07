from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-qa-guard",
    version="2.0.0",
    author="Agentic-Eval Security Team",
    author_email="security@agentic-eval.com",
    description="Sub-millisecond OWASP LLM Top 10 Security & Trajectory Auditor for Autonomous AI Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivegotahunnitonit/agentic-eval",
    packages=find_packages(),
    py_modules=["agent_qa_guard"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Business Source License 1.1 (BSL 1.1)",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0",
        "cryptography>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "agent-qa-guard=agent_qa_guard:main",
        ],
    },
)
