from typing import List, Sequence

# For demonstration, we hard-code the dictionary snippet here.
DICT_SNIPPET = [
    ("ABACUS", ["AE", "B", "AH", "K", "AH", "S"]),
    ("BOOK",   ["B", "UH", "K"]),
    ("THEIR",  ["DH", "EH", "R"]),
    ("THERE",  ["DH", "EH", "R"]),
    ("TOMATO", ["T", "AH", "M", "AA", "T", "OW"]),
    ("TOMATO", ["T", "AH", "M", "EY", "T", "OW"]),
]

def find_word_combos_with_pronunciation(
    phonemes: Sequence[str],
    dictionary: List[tuple] = DICT_SNIPPET
) -> List[List[str]]:
    """
    Given a sequence of phonemes (e.g. ["DH", "EH", "R", "DH", "EH", "R"]),
    find all combinations of words (from 'dictionary') that exactly match
    this phoneme sequence in order.
    
    Args:
        phonemes: The input list of phonemes.
        dictionary: A list of (word, [phoneme...]) tuples. Defaults to DICT_SNIPPET.
        
    Returns:
        A list of all possible word combinations (each combination is a list of strings).
    """
    results = []
    partial = []

    def backtrack(i: int):
        # If we've consumed all the phonemes, we have a complete match.
        if i == len(phonemes):
            results.append(partial[:])  # copy current combination
            return
        
        # Otherwise, try each word in the dictionary
        for (word, phone_list) in dictionary:
            L = len(phone_list)
            
            # Check if we can match phone_list at position i
            if i + L <= len(phonemes) and phonemes[i : i + L] == phone_list:
                partial.append(word)
                backtrack(i + L)
                partial.pop()
    
    backtrack(0)
    return results

