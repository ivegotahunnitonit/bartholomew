import os
import json
import time
from typing import List, Dict, Any

class SyntheticDatasetFactory:
    """
    SYNTHETIC AI TRAINING DATASET FACTORY v1.0
    Generates high-value, specialized training datasets for fine-tuning LLMs 
    and AI agents on Code Remediation, Secret Scrubbing, and Tool Trajectories.
    Formatted for Hugging Face Datasets & OpenAI Fine-Tuning (JSONL).
    """
    def __init__(self, output_dir: str = "datasets"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_agent_qa_dataset(self, num_samples: int = 100) -> str:
        """Generates structured code-fix & trajectory evaluation dataset."""
        filename = os.path.join(self.output_dir, "agent_qa_code_fixes.jsonl")
        
        sample_templates = [
            {
                "instruction": "Identify and fix unmasked credential logging in the Python step dispatcher.",
                "buggy_code": "def log_step(step_name, api_key):\n    print(f'[STEP {step_name}] Using API key: {api_key}')",
                "fixed_code": "def log_step(step_name, api_key):\n    masked_key = api_key[:4] + '***' if api_key else 'NONE'\n    print(f'[STEP {step_name}] Using API key: {masked_key}')",
                "category": "SECRET_SCRUBBING",
                "severity": "CRITICAL"
            },
            {
                "instruction": "Fix silent exception swallowing in DOM automation loop.",
                "buggy_code": "try:\n    element.click()\nexcept Exception:\n    return None",
                "fixed_code": "try:\n    element.click()\nexcept Exception as e:\n    logger.error(f'DOM click failed on {element}: {e}')\n    raise ElementInteractionError(f'Failed to click {element}') from e",
                "category": "ERROR_HANDLING",
                "severity": "MEDIUM"
            },
            {
                "instruction": "Prevent infinite tool execution loops in agent step planner.",
                "buggy_code": "while True:\n    action = agent.decide()\n    action.execute()",
                "fixed_code": "MAX_TURNS = 10\nfor turn in range(MAX_TURNS):\n    action = agent.decide()\n    if action.is_complete():\n        break\n    action.execute()\nelse:\n    raise MaxTurnsExceededError('Agent reached maximum 10-turn limit')",
                "category": "RECURSION_GUARD",
                "severity": "HIGH"
            }
        ]

        records = []
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(num_samples):
                template = sample_templates[i % len(sample_templates)]
                record = {
                    "id": f"acn-ds-{i+1:05d}",
                    "messages": [
                        {"role": "system", "content": "You are an expert AI agentic QA engineer. Identify and fix security vulnerabilities, silent error swallowing, and infinite loops in agent codebases."},
                        {"role": "user", "content": f"{template['instruction']}\n\nCode snippet:\n```python\n{template['buggy_code']}\n```"},
                        {"role": "assistant", "content": f"Here is the security-hardened remediation:\n\n```python\n{template['fixed_code']}\n```\n\n**Category:** `{template['category']}` | **Severity:** `{template['severity']}`"}
                    ],
                    "metadata": {
                        "category": template["category"],
                        "severity": template["severity"],
                        "synthetic": True,
                        "provider": "ACN Data Factory v1.0"
                    }
                }
                f.write(json.dumps(record) + "\n")
                records.append(record)

        # Write dataset metadata manifest
        meta_filename = os.path.join(self.output_dir, "dataset_metadata.json")
        metadata = {
            "dataset_name": "ACN Agentic QA & Code Remediation Instruction Dataset",
            "version": "1.0.0",
            "total_records": num_samples,
            "format": "JSONL (OpenAI / Hugging Face Compatible)",
            "license": "Commercial / MIT Sample",
            "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "categories": ["SECRET_SCRUBBING", "ERROR_HANDLING", "RECURSION_GUARD"],
            "target_valuation": "$500 - $2,500 per enterprise lab license"
        }
        with open(meta_filename, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return filename

dataset_factory = SyntheticDatasetFactory()
if __name__ == "__main__":
    filepath = dataset_factory.generate_agent_qa_dataset(num_samples=150)
    print(f"[SUCCESS] Generated synthetic dataset at: {filepath}")

