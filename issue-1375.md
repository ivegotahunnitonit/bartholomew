# _**Summary**_

The MemoryParsingService includes an ambiguity guard intended to filter out weak fact classifications and push them to the fuzzy matching fallback. However, this guard is systemically bypassed for most English sentences due to the inclusion of extremely common auxiliary verbs (is, are, was, were) in the STRONG_FACT_PATTERNS list. This leads to incorrect memory type classifications (e.g., misclassifying items with typos as fact instead of their correct type like decision).


# **_Steps to Reproduce_**

**_1.*_* Initialize the MemoryParsingService.

**_2._** Parse a memory containing a weak factual verb (e.g., "uses") alongside a misspelled keyword from another category (e.g., "decded" for decision), and include the word "is".

- **Input 1:** "The project uses Django and it is maintained, and we decded on Postgres"

_**3.**_ Parse the same sentence but replace "is" with a non-matching word like "gets".

- **_Input 2:_** "The project uses Django and it gets maintained, and we decded on Postgres"

_**4.**_ Observe the resolved memory types.


# **_Minimal Reproduction Code:_**

> from memanto.app.core import MemoryRecord
> from memanto.app.services.memory_parsing_service import MemoryParsingService
> 
> parser = MemoryParsingService()
> 
> #Scenario 1: Contains 'is'
> mem1 = MemoryRecord(content="The project uses Django and it is maintained, and we decded on Postgres", type=None, title="t", actor_id="u", source="s", agent_id="a")
> parser.parse_memory(mem1)
> print(f"Result 1 (with 'is'): {mem1.type}")
> 
> #Scenario 2: Does not contain 'is' (replaced with 'gets')
> mem2 = MemoryRecord(content="The project uses Django and it gets maintained, and we decded on Postgres", type=None, title="t", actor_id="u", source="s", agent_id="a")
> parser.parse_memory(mem2)
> print(f"Result 2 (without 'is'): {mem2.type}")


# **_Expected Behavior_**

Both inputs should trigger the Ambiguity Guard because the fact score is low (fact_max < 4 matching only "uses"), then fall back to the fuzzy matching logic, and be classified as decision (successfully resolving the typo "decded").


# **_Actual Behavior_**

- Input 1 (with 'is'): Classified as fact (Incorrect).
- Input 2 (without 'is'): Classified as decision (Correct).

The guard was bypassed in Input 1 simply because of the presence of the word "is".


# **_Root Cause Analysis_**

- The Ambiguity Guard only triggers for weak fact classifications (fact_max < 4) if no strong factual patterns are detected in the text:

> if fact_max < 4 and not any(
>     pattern.search(text) for pattern in self.STRONG_FACT_PATTERNS
> ):
>     return None

- In memanto/app/services/memory_parsing_service.py, the STRONG_FACT_PATTERNS contains:

> r"\b(?:is|are|was|were)\b"

Because is, are, was, and were are among the most common auxiliary verbs in English, this pattern matches almost every standard sentence. As a result, the guard condition evaluates to False for almost all English inputs containing these verbs, letting weak signals pass through as fact and bypassing the fuzzy fallback mechanism.

# **_Suggested Fix_**

Remove r"\b(?:is|are|was|were)\b" from the STRONG_FACT_PATTERNS list.

More specific state-declarative structures (e.g., is called, are located, was enabled) are already mapped with a high confidence score of 4 under RULES["fact"]. Standalone auxiliary verbs are too weak to be considered strong indicators of a fact and should not bypass the ambiguity check.
