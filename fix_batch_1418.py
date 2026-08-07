#!/usr/bin/env python3
"""Fix batch_store_memories validation bypass in memory_write_service.py"""

with open('memanto/app/services/memory_write_service.py', 'r') as f:
    content = f.read()

old = (
    "                    # skip validation for speed\n"
    "                    ## Validate memory\n"
    "                    # validation_result = self.validation_service.validate_memory(memory, context)\n"
    "                    ## Use validated memory if modified\n"
    "                    # if \"memory\" in validation_result:\n"
    "                    #     memory = validation_result[\"memory\"]\n"
    "                    validation_result = {\n"
    "                        \"action\": \"store\",\n"
    "                        \"reason\": \"Stored without conflict — no context provided.\",\n"
    "                    }"
)
new = (
    "                    # Run conflict-detection validation for each memory in the batch.\n"
    "                    validation_result = self.validation_service.validate_memory(\n"
    "                        memory, context\n"
    "                    )\n"
    "                    # If validation modified the memory (e.g. status -> provisional),\n"
    "                    # use the updated copy for storage.\n"
    "                    if \"memory\" in validation_result:\n"
    "                        memory = validation_result[\"memory\"]"
)

if old in content:
    content = content.replace(old, new, 1)
    with open('memanto/app/services/memory_write_service.py', 'w') as f:
        f.write(content)
    print("FIXED batch_store_memories validation bypass")
else:
    print("Pattern not found - checking for alternate form...")
    # Show what's around line 188
    lines = content.split('\n')
    for i, line in enumerate(lines[185:200], start=186):
        print(f"{i}: {repr(line)}")
