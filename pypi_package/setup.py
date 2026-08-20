from setuptools import setup, find_packages

setup(
    name="bartholomew-eval",
    version="9.1.0",
    author="Bartholomew AI Contributors",
    author_email="help@bartholomew.info",
    description="Sub-millisecond OWASP LLM Top 10 Security Guard, Sovereign AES-256 Memory & Universal Swarm Federation Engine for AI Agents",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ivegotahunnitonit/bartholomew",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0"
    ],
    entry_points={
        "console_scripts": [
            "bartholomew=bartholomew_eval.cli:main",
            "bartholomew-eval=bartholomew_eval.cli:main",
            "bartholomew-verify=bartholomew_eval.attestation_verifier:main",
            "bartholomew-scout=bartholomew_eval.agent_scouter:main",
            "bartholomew-swarm=bartholomew_eval.swarm_federation:main",
        ],
    },
)
