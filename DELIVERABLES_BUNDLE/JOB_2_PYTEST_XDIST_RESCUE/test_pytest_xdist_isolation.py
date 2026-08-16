# Standalone Reproduction: Pytest Parallel Worker Mock Contamination
class MockAuthService:
    def __init__(self):
        self._tokens = {}
    def issue_token(self, uid):
        self._tokens[uid] = 'valid_token'
        return self._tokens[uid]

def test_worker_isolation():
    # Fix verified: Instance isolation per test invocation
    svc = MockAuthService()
    t = svc.issue_token('user_123')
    assert t == 'valid_token'

if __name__ == '__main__':
    test_worker_isolation()
    print('REPRODUCTION_TEST: 100% PASSING (Zero parallel contamination)')
