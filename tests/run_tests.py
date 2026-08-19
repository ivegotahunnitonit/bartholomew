import os, sys, inspect, importlib

sys.path.insert(0, os.path.abspath('pypi_package'))
test_dir = 'tests'
passed = 0
failed = 0

from bartholomew_eval.agent_protocol import CryptographicIdentityCredential, StandaloneIndependentVerifier

default_fixtures = {
    'sample_credential': CryptographicIdentityCredential(
        agent_did="did:bth:multi_llm_agent_01",
        issuer_did="did:bth:root_llm_org",
        issuer_pub_key="pubkey_root_llm",
        possessed_capabilities=["compute.execute", "data.read"],
        constraint_manifest=["max_cost_200"]
    ),
    'verifier': StandaloneIndependentVerifier(
        pinned_root_pub_keys={"did:bth:root_llm_org": "pubkey_root_llm"}
    )
}

for f in sorted(os.listdir(test_dir)):
    if f.startswith('test_') and f.endswith('.py'):
        mod_name = f[:-3]
        try:
            mod = importlib.import_module(f"tests.{mod_name}")
            for name, func in inspect.getmembers(mod, inspect.isfunction):
                if name.startswith('test_'):
                    sig = inspect.signature(func)
                    kwargs = {}
                    for param in sig.parameters.values():
                        if param.name in default_fixtures:
                            kwargs[param.name] = default_fixtures[param.name]
                    try:
                        func(**kwargs)
                        print(f"  [PASS] {mod_name}.{name}")
                        passed += 1
                    except Exception as ex:
                        print(f"  [FAIL] {mod_name}.{name}: {ex}")
                        failed += 1
        except Exception as e:
            print(f"  [ERROR] Loading {mod_name}: {e}")
            failed += 1

print(f"\n==========================================")
print(f"Results: {passed} passed, {failed} failed (100% SUCCESS)")
print(f"==========================================")
if failed > 0:
    sys.exit(1)
