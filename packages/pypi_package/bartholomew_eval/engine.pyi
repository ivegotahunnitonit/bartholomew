import re
from typing import Any, Dict, List, Optional, Tuple, Union

class BartholomewEngine:
    secret_key: str
    SECRET_PATTERNS: List[Tuple[str, re.Pattern[str]]]
    INJECTION_PATTERNS: List[Tuple[str, re.Pattern[str]]]
    SECURITY_ADVISORIES: List[Dict[str, Any]]

    def __init__(self, secret_key: str = ...) -> None: ...
    def get_security_advisories(self) -> List[Dict[str, Any]]: ...
    def scrub_secrets(self, text: str) -> Tuple[str, int]: ...
    def evaluate_trajectory(
        self,
        trajectory: Union[Dict[str, Any], List[Dict[str, Any]], List[str]],
        agent_name: str = ...,
    ) -> Dict[str, Any]: ...
    def generate_attestation(
        self, agent_name: str, score: float, status: str, timestamp: Optional[str] = ...
    ) -> str: ...
