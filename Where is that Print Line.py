import re

def list_print_statements(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    print_statements = []
    function_name = None
    
    for i, line in enumerate(lines):
        # Check if the line is a function definition
        function_match = re.match(r'^\s*def\s+(\w+)\s*\(', line)
        if function_match:
            function_name = function_match.group(1)
        
        # Check if the line contains a print statement
        if 'print(' in line:
            print_statements.append({
                'line_number': i + 1,
                'function': function_name,
                'statement': line.strip()
            })
    
    return print_statements

# Path to your Python file
file_path = 'hatchery.py'  # Update this to the correct path of your file

# Get the list of print statements
print_statements = list_print_statements(file_path)

# Print the results
for statement in print_statements:
    print(f"Line {statement['line_number']} in function {statement['function']}: {statement['statement']}")

