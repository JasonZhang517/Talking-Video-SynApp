import numpy as np

def smith_waterman(a: str, b: str, alignment_score: float = 1, gap_cost: float = 1) -> float:
    """
    Compute the Smith-Waterman alignment score for two strings.
    See https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm#Algorithm
    This implementation has a fixed gap cost (i.e. extending a gap is considered
    free). In the terminology of the Wikipedia description, W_k = {c, c, c, ...}.
    This implementation also has a fixed alignment score, awarded if the relevant
    characters are equal.
    Kinda slow, especially for large (50+ char) inputs.
    """
    # H holds the alignment score at each point, computed incrementally
    H = np.zeros((len(a) + 1, len(b) + 1))
    for i in range(1, len(a) + 1):
      for j in range(1, len(b) + 1):
        # The score for substituting the letter a[i-1] for b[j-1]. Generally low
        # for mismatch, high for match.
        match = H[i - 1, j - 1] + (alignment_score if a[i - 1] == b[j - 1] else 0)
        # The scores for for introducing extra letters in one of the strings (or
        # by symmetry, deleting them from the other).
        delete = H[1: i, j].max() - gap_cost if i > 1 else 0
        insert = H[i, 1: j].max() - gap_cost if j > 1 else 0
        H[i,j] = max(match, delete, insert, 0)
    # The highest score is the best local alignment.
    # For our purposes, we don't actually care _what_ the alignment was, just how
    # aligned the two strings were.
    return H.max()


def precision(instruction, content):
    match = 0
    for word in instruction:
        if word in content:
            match += 1
    return match / len(instruction)


def merge_asr_segments(result):
    """
    Merge ASR results from AiSpeech.
    """
    merged_result = []
    cur_bg = result[0]["bg"]
    cur_ed = result[0]["ed"]
    cur_onebest = result[0]["onebest"]
    for idx, segment in enumerate(result[1:]):
         bg = segment["bg"]
         ed = segment["ed"]
         onebest = segment["onebest"]
         if bg > cur_ed:
             merged_result.append({"bg": cur_bg, "ed": cur_ed, "onebest": cur_onebest})
             cur_bg = bg
             cur_ed = ed
             cur_onebest = onebest
         elif bg == cur_ed:
             cur_ed = ed
             cur_onebest += onebest
         if idx == len(result) - 2:
             merged_result.append({"bg": cur_bg, "ed": cur_ed, "onebest": cur_onebest})
        
    return merged_result
