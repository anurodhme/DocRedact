import re

text1 = "Call me at (555) 123-4567 or +1-800-999-8888."
text2 = """
John Smith lives at 123 Main St, New York.
Contact: john.smith@email.com | Phone: (212) 555-1234.
Card: 4000-1234-5678-9012.
"""

# Your current phone regex pattern
phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'

print("Current phone pattern:", phone_pattern)
print()

print("Testing text1:")
matches1 = list(re.finditer(phone_pattern, text1))
for match in matches1:
    print(f"  Found: '{match.group()}' at position {match.start()}-{match.end()}")

print()
print("Testing text2:")
matches2 = list(re.finditer(phone_pattern, text2))
for match in matches2:
    print(f"  Found: '{match.group()}' at position {match.start()}-{match.end()}")

print()
print("All matches in text1:", re.findall(phone_pattern, text1))
print("All matches in text2:", re.findall(phone_pattern, text2))

# Test specific phone numbers from the failing tests
print()
print("Testing specific numbers from failing tests:")
test_numbers = ["(555) 123-4567", "+1-800-999-8888", "(212) 555-1234"]
for number in test_numbers:
    match = re.fullmatch(phone_pattern, number)
    print(f"  {number}: {'MATCH' if match else 'NO MATCH'}")
