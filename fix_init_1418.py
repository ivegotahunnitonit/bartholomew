#!/usr/bin/env python3
"""
Add validation_service lazy property to MemoryWriteService
and fix the init to set _validation_service = None
"""

with open('memanto/app/services/memory_write_service.py', 'r') as f:
    content = f.read()

# Add _validation_service init in __init__
old_init = (
    "        self.client = moorcheh_client\n"
    "        self._parser = MemoryParsingService()\n"
    "        self._namespace_service = None\n"
)
new_init = (
    "        self.client = moorcheh_client\n"
    "        self._parser = MemoryParsingService()\n"
    "        self._namespace_service = None\n"
    "        self._validation_service = None\n"
)

# Add lazy property before @property namespace_service
old_prop = (
    "    @property\n"
    "    def namespace_service(self):\n"
    "        \"\"\"Lazily create the namespace service used for memory scopes.\"\"\"\n"
)
new_prop = (
    "    @property\n"
    "    def validation_service(self):\n"
    "        \"\"\"Lazily create the validation service for conflict detection.\"\"\"\n"
    "        if self._validation_service is None:\n"
    "            from memanto.app.legacy.memory_validation_service import MemoryValidationService\n"
    "            self._validation_service = MemoryValidationService(self.client)\n"
    "        return self._validation_service\n"
    "\n"
    "    @property\n"
    "    def namespace_service(self):\n"
    "        \"\"\"Lazily create the namespace service used for memory scopes.\"\"\"\n"
)

if old_init in content:
    content = content.replace(old_init, new_init, 1)
    print("FIXED __init__: added _validation_service = None")
else:
    print("SKIP __init__: pattern not found")

if old_prop in content:
    content = content.replace(old_prop, new_prop, 1)
    print("FIXED: added validation_service lazy property")
else:
    print("SKIP lazy property: pattern not found")

with open('memanto/app/services/memory_write_service.py', 'w') as f:
    f.write(content)

print("Done.")
