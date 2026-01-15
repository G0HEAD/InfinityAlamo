# InfinityAlamo Issue #2: parse_fields TDD Edge Cases & Regex Improvements

**Agent:** Claude (Strategist/QA)
**Date:** 2026-01-15
**Status:** Analysis Complete

---

## Executive Summary

I've expanded the `test_parse_fields.py` test suite with **7 new edge-case tests** and identified **3 critical regex bugs** in the current implementation. The main issue: **name patterns are overly greedy and capture multi-line text**, breaking field extraction.

**Test Results:**
- ✅ 4 edge-case tests passing (partial match, missing fields, special chars)
- ❌ 5 tests failing due to regex bugs (greedy pattern matching)

---

## Part 1: Edge Case Tests Added

### Test Suite Expansion (7 New Tests)

#### ✅ **Test 1: `test_parse_fields_names_with_apostrophes_and_hyphens()`**
**Purpose:** Verify handling of special characters in names (O'Brien, Mary-Jane)
**Status:** PASSING (documents expected truncation behavior)
**Current Behavior:** Names are truncated at apostrophes/hyphens as documented
**Future Enhancement:** Improve regex to capture full names with special chars

```python
# Current: "Patrick O'Brien Jr." → "Patrick O"
# Desired: "Patrick O'Brien Jr." → "Patrick O'Brien Jr."
```

#### ❌ **Test 2: `test_parse_fields_case_number_lowercase()`**
**Purpose:** Test lowercase case numbers (demo-2026-0001)
**Status:** FALSE FAILURE (test expectation was wrong)
**Finding:** Case numbers with lowercase letters **actually work** due to `re.IGNORECASE` flag
**Action Required:** Fix test assertion (current implementation is correct!)

#### ✅ **Test 3: `test_parse_fields_missing_all_fields()`**
**Purpose:** Verify graceful handling when no fields are present
**Status:** PASSING
**Result:** All fields correctly return `None`, notes track "no match"

#### ❌ **Test 4: `test_parse_fields_extra_whitespace()`**
**Purpose:** Test whitespace stripping (leading/trailing/internal spaces)
**Status:** FAILING
**Issue:** Greedy pattern captures newlines + next label
**Example:** `"Jane Executor   \nProperty Address"` instead of `"Jane Executor"`

#### ❌ **Test 5: `test_parse_fields_names_with_suffixes()`**
**Purpose:** Test generational suffixes (Jr., Sr., III, IV)
**Status:** FAILING
**Issue:** Greedy pattern captures newlines
**Example:** `"Robert James Smith III\nPetitioner"` instead of `"Robert James Smith III"`

#### ✅ **Test 6: `test_parse_fields_address_with_special_characters()`**
**Purpose:** Test addresses with #, &, apartment numbers
**Status:** PASSING
**Result:** Address pattern `[^\n]+` correctly handles all special chars

#### ✅ **Test 7: `test_parse_fields_partial_match_scenario()`**
**Purpose:** Test extraction when only some fields are present
**Status:** PASSING
**Result:** Correctly extracts available fields, returns `None` for missing ones

---

## Part 2: Regex Pattern Analysis

### Current Patterns (from `parse_fields.py`)

| Field | Pattern | Issue Identified |
|-------|---------|------------------|
| **Case Number** | `r"Case Number:\s*([A-Z0-9\-]+)"` | ❌ **Uppercase-only** (actually OK due to re.IGNORECASE) |
| **Filing Date** | `r"Filing Date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})"` | ✅ Works correctly |
| **Deceased Name** | `r"Deceased:\s*([A-Za-z\.\s]+)"` | ❌ **CRITICAL: `\s` matches newlines!** |
| **Filer Name** | `r"Petitioner:\s*([A-Za-z\.\s]+)"` | ❌ **CRITICAL: `\s` matches newlines!** |
| **Property Address** | `r"Property Address:\s*([^\n]+)"` | ✅ Works correctly |

### Root Cause: Greedy `\s` in Name Patterns

The pattern `[A-Za-z\.\s]+` uses `\s` which matches:
- Spaces (intended) ✅
- Tabs (intended) ✅
- **Newlines** (NOT intended) ❌
- Carriage returns (NOT intended) ❌

This causes the regex to capture beyond the intended field, including the next label and beyond.

**Example Failure:**
```
Input:  "Deceased: John Q. Doe\nPetitioner: Jane\n"
Current: "John Q. Doe\nPetitioner"  ❌
Expected: "John Q. Doe"  ✅
```

---

## Part 3: Proposed Regex Improvements

### 🔧 **Fix 1: Replace `\s` with ` ` (space) in Name Patterns**

**Current (Broken):**
```python
r"Deceased:\s*([A-Za-z\.\s]+)"
r"Petitioner:\s*([A-Za-z\.\s]+)"
```

**Proposed (Fixed):**
```python
r"Deceased:\s*([A-Za-z\. ]+)"   # Space instead of \s in capture group
r"Petitioner:\s*([A-Za-z\. ]+)"
```

**Why:** Using literal space ` ` instead of `\s` prevents matching newlines while still allowing multiple spaces in names.

---

### 🚀 **Fix 2: Enhanced Name Pattern (Support Special Characters)**

**Proposed (Comprehensive):**
```python
# Support: letters, spaces, dots, apostrophes, hyphens, accented chars
r"Deceased:\s*([A-Za-zÀ-ÿ\.\-\'\s]+?)(?:\n|$)"
r"Petitioner:\s*([A-Za-zÀ-ÿ\.\-\'\s]+?)(?:\n|$)"
```

**Enhancements:**
- `À-ÿ`: Accented/Latin characters (José, François)
- `\-`: Hyphens (Mary-Jane, Smith-Jones)
- `\'`: Apostrophes (O'Brien, D'Angelo)
- `+?`: Non-greedy quantifier (stops at first newline)
- `(?:\n|$)`: Explicit boundary (newline or end-of-string)

**Note:** If `\s` is kept in the pattern, use `+?` (non-greedy) instead of `+` (greedy):
```python
r"Deceased:\s*([A-Za-zÀ-ÿ\.\-\'\s]+?)(?:\n|$)"
#                                  ^ non-greedy stops at newline boundary
```

---

### 🔧 **Fix 3: Case Number Pattern (Already Works, Just Clarify)**

**Current:**
```python
r"Case Number:\s*([A-Z0-9\-]+)"   # Uppercase only in pattern
```

**Status:** ✅ **Actually works for lowercase** due to `re.IGNORECASE` flag in `_first_match()`

**Recommended (Optional Clarity):**
```python
r"Case Number:\s*([A-Za-z0-9\-]+)"   # Explicit mixed-case support
```

**Why:** Makes intent clearer even though `re.IGNORECASE` already handles this.

---

### 🔧 **Fix 4: Filing Date Pattern (Add Alternate Formats)**

**Current (Strict YYYY-MM-DD only):**
```python
r"Filing Date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})"
```

**Proposed (Support MM/DD/YYYY and flexible separators):**
```python
# Keep primary pattern as-is, add alternates:
[
    r"Filing Date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",           # YYYY-MM-DD
    r"Filing Date:\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})",       # MM/DD/YYYY
    r"Filed:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",                 # Alternate label
    r"Filed:\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})",             # Alternate label + format
]
```

**Note:** This requires post-processing to normalize dates to YYYY-MM-DD format in `_clean()` or a new helper.

---

## Part 4: Recommended Implementation Plan

### Phase 1: Critical Fixes (Immediate) 🔥

**Priority:** High - These fixes resolve failing tests

1. **Fix name patterns** to use literal space instead of `\s`:
   ```python
   # In src/probate/pdf/parse_fields.py
   deceased_name = _first_match(
       text,
       [
           r"Deceased:\s*([A-Za-z\. ]+)",    # Changed \s to space in capture
           r"Decedent:\s*([A-Za-z\. ]+)",    # Changed \s to space in capture
       ],
       notes,
       "deceased_name",
   )

   filer_name = _first_match(
       text,
       [
           r"Petitioner:\s*([A-Za-z\. ]+)",  # Changed \s to space in capture
           r"Executor:\s*([A-Za-z\. ]+)",    # Changed \s to space in capture
       ],
       notes,
       "filer_name",
   )
   ```

2. **Update test expectations** in `test_parse_fields_case_number_lowercase()`:
   ```python
   # Fix: Test expectation was wrong (lowercase actually works)
   assert fields.case_number == "demo-2026-0001"  # Not None
   assert "case_number: matched" in fields.notes  # Not "no match"
   ```

3. **Run tests again** to verify fixes:
   ```bash
   pytest tests/test_parse_fields.py -v
   ```

**Expected Result After Phase 1:** All 9 tests should pass ✅

---

### Phase 2: Enhanced Pattern Support (Follow-up) 🚀

**Priority:** Medium - Adds robustness for real-world data

4. **Add special character support** to name patterns:
   ```python
   r"Deceased:\s*([A-Za-zÀ-ÿ\.\-\' ]+?)(?:\n|$)"
   #              ^^^^^^ accented  ^^ hyphen/apostrophe
   #                                  ^^ non-greedy  ^^^^ boundary
   ```

5. **Add tests for enhanced patterns**:
   - Names with accented characters (José García)
   - Multi-word hyphenated names (Mary-Jane Smith-Jones)
   - Full apostrophe names (Patrick O'Brien Jr.)

6. **Add alternate date format support** (if needed by real-world PDFs):
   - MM/DD/YYYY pattern
   - Date normalization helper

---

### Phase 3: Confidence Scoring (Future) 🔮

**Priority:** Low - Nice to have, not blocking

7. **Add confidence scoring** per field:
   - Track which pattern matched (already in notes)
   - Add numeric confidence (0.0-1.0) based on pattern quality
   - Flag low-confidence extractions for manual review

8. **Example schema extension**:
   ```python
   @dataclass
   class ExtractedFields:
       deceased_name: Optional[str]
       deceased_name_confidence: float = 0.0  # New
       # ... etc
   ```

---

## Part 5: Test Results Summary

### Before Fixes (Current State)

```
tests/test_parse_fields.py::test_parse_fields_primary_labels FAILED      [ 11%]
tests/test_parse_fields.py::test_parse_fields_alternate_labels FAILED    [ 22%]
tests/test_parse_fields.py::test_parse_fields_names_with_apostrophes_and_hyphens PASSED [ 33%]
tests/test_parse_fields.py::test_parse_fields_case_number_lowercase FAILED [ 44%]
tests/test_parse_fields.py::test_parse_fields_missing_all_fields PASSED  [ 55%]
tests/test_parse_fields.py::test_parse_fields_extra_whitespace FAILED    [ 66%]
tests/test_parse_fields.py::test_parse_fields_names_with_suffixes FAILED [ 77%]
tests/test_parse_fields.py::test_parse_fields_address_with_special_characters PASSED [ 88%]
tests/test_parse_fields.py::test_parse_fields_partial_match_scenario PASSED [100%]

Result: 5 failed, 4 passed in 0.09s
```

### After Phase 1 Fixes (Expected)

```
tests/test_parse_fields.py::test_parse_fields_primary_labels PASSED      [ 11%]
tests/test_parse_fields.py::test_parse_fields_alternate_labels PASSED    [ 22%]
tests/test_parse_fields.py::test_parse_fields_names_with_apostrophes_and_hyphens PASSED [ 33%]
tests/test_parse_fields.py::test_parse_fields_case_number_lowercase PASSED [ 44%]
tests/test_parse_fields.py::test_parse_fields_missing_all_fields PASSED  [ 55%]
tests/test_parse_fields.py::test_parse_fields_extra_whitespace PASSED    [ 66%]
tests/test_parse_fields.py::test_parse_fields_names_with_suffixes PASSED [ 77%]
tests/test_parse_fields.py::test_parse_fields_address_with_special_characters PASSED [ 88%]
tests/test_parse_fields.py::test_parse_fields_partial_match_scenario PASSED [100%]

Result: 9 passed in 0.09s ✅
```

---

## Part 6: Key Findings & Recommendations

### 🔴 Critical Issues Found

1. **Greedy `\s` pattern in names** - Captures newlines and subsequent labels
2. **No boundary enforcement** - Patterns don't stop at logical field boundaries
3. **Test coverage gap** - Original tests didn't catch multi-line capture bug

### ✅ Positive Findings

1. **`re.IGNORECASE` works as intended** - Case numbers already support lowercase
2. **Address pattern is robust** - `[^\n]+` correctly handles special characters
3. **Missing field handling is solid** - Returns `None` gracefully, tracks in notes

### 🎯 Recommendations for Cursor (Builder)

When implementing fixes:

1. **Start with Phase 1 fixes** - These are minimal, safe changes
2. **Test after each change** - Run `pytest tests/test_parse_fields.py -v`
3. **Don't over-engineer** - Stick to documented patterns first, enhance later
4. **Consider real PDF data** - Once you have sample PDFs from the portal, validate patterns against actual text

### 📋 Recommendations for OpenCode (Orchestrator)

1. **Gate Phase 2 on real data** - Wait for actual probate PDF samples before adding special character support
2. **Phase 3 is optional** - Confidence scoring can wait until after MVP deployment
3. **Monitor extraction quality** - Track `notes` field in production to identify pattern misses

---

## Appendix A: Example Regex Playground

### Test the Greedy Bug

**Python REPL:**
```python
import re

text = "Deceased: John Q. Doe\nPetitioner: Jane\n"

# Current (broken)
pattern_broken = r"Deceased:\s*([A-Za-z\.\s]+)"
match = re.search(pattern_broken, text, re.IGNORECASE)
print(match.group(1))  # "John Q. Doe\nPetitioner"  ❌

# Fixed (using literal space)
pattern_fixed = r"Deceased:\s*([A-Za-z\. ]+)"
match = re.search(pattern_fixed, text, re.IGNORECASE)
print(match.group(1))  # "John Q. Doe"  ✅

# Enhanced (non-greedy with boundary)
pattern_enhanced = r"Deceased:\s*([A-Za-z\.\s]+?)(?:\n|$)"
match = re.search(pattern_enhanced, text, re.IGNORECASE)
print(match.group(1))  # "John Q. Doe"  ✅
```

---

## Appendix B: Files Modified

### New Files Created
- `REGEX_IMPROVEMENTS_PROPOSAL.md` (this document)

### Modified Files
- `tests/test_parse_fields.py` - Added 7 new edge-case tests (lines 36-198)

### Files to Modify (Recommended)
- `src/probate/pdf/parse_fields.py` - Apply regex fixes (lines 31-49)

---

## Appendix C: Definition of Done Checklist

- [x] Added at least 4 edge-case tests (added 7)
- [x] Identified regex pattern issues
- [x] Proposed specific regex improvements
- [x] Documented current vs. expected behavior
- [x] Created phased implementation plan
- [x] Prepared findings for GitHub issue #2
- [ ] Posted findings to GitHub (next step)
- [ ] Updated GitHub status to done (final step)

---

**Ready for Review by OpenCode & Cursor**

This analysis provides a clear path forward for fixing the parse_fields implementation. The critical fixes (Phase 1) should be implemented immediately, while enhanced support (Phase 2) can wait for real-world PDF samples.

---

*Generated by Claude (InfinityAlamo QA/Strategist)*
*InfinityAlamo Issue #2: parse_fields TDD Expansion*
