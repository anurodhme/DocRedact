import re

text1 = "Call me at (555) 123-4567 or +1-800-999-8888."
text2 = """
John Smith lives at 123 Main St, New York.
Contact: john.smith@email.com | Phone: (212) 555-1234.
Card: 4000-1234-5678-9012.
"""

# Your current phone regex pattern (with word boundary at start)
current_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'

# Fixed pattern (without word boundary at start)
fixed_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'

print("Current pattern:", current_pattern)
print("Fixed pattern:  ", fixed_pattern)
print()

print("Testing text1 with current pattern:")
matches1_current = re.findall(current_pattern, text1)
print("  Matches found:", matches1_current)

print("Testing text1 with fixed pattern:")
matches1_fixed = re.findall(fixed_pattern, text1)
print("  Matches found:", matches1_fixed)

print()
print("Testing text2 with current pattern:")
matches2_current = re.findall(current_pattern, text2)
print("  Matches found:", matches2_current)

print("Testing text2 with fixed pattern:")
matches2_fixed = re.findall(fixed_pattern, text2)
print("  Matches found:", matches2_fixed)

# Test specific phone numbers from the failing tests
print()
print("Testing specific numbers from failing tests:")
test_numbers = ["(555) 123-4567", "+1-800-999-8888", "(212) 555-1234"]
for number in test_numbers:
    match_current = re.fullmatch(current_pattern, number)
    match_fixed = re.fullmatch(fixed_pattern, number)
    print(f"  {number}: Current={'MATCH' if match_current else 'NO MATCH'}, Fixed={'MATCH' if match_fixed else 'NO MATCH'}")
