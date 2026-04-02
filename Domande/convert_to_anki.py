#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert Metodologia.md to Anki CSV format (Italian kept).
Parses markdown questions with format:
- [x] for correct answers
- [ ] for incorrect answers

Output format (semicolon separated):
Field 1 (Question in Italian); Q1; Q2; Q3; Q4; Q5 (empty); Answer (1000, 0100, 0010, 0001)
"""

import re

def parse_question_block(lines, start_idx):
    """Parse a single question block from markdown."""
    i = start_idx
    
    # Skip empty lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    
    if i >= len(lines):
        return None, i
    
    # Check for question header (## Number - Metodologia)
    header_match = re.match(r'^##\s*\d+\s*-\s*Metodologia', lines[i])
    if not header_match:
        return None, i + 1
    
    i += 1
    
    # Skip empty lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    
    if i >= len(lines):
        return None, i
    
    # Get question text (should be in bold)
    question_line = lines[i].strip()
    question_match = re.match(r'^\*\*(.+?)\*\*$', question_line)
    if question_match:
        question = question_match.group(1)
    else:
        # Handle case where question might be plain text
        question = question_line.lstrip('#* ')
    
    i += 1
    
    # Skip empty lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    
    # Collect answers (4 answers expected)
    answers = []
    correct_idx = -1
    
    for ans_idx in range(4):
        if i >= len(lines):
            break
            
        line = lines[i].strip()
        
        # Check for correct answer [x]
        if line.startswith('- [x]'):
            correct_idx = ans_idx
            answer_text = line[5:].strip()
            # Remove A., B., C., D. prefix if present
            answer_text = re.sub(r'^[A-D]\.\s*', '', answer_text)
            answers.append(answer_text)
        elif line.startswith('- [ ]'):
            answer_text = line[5:].strip()
            # Remove A., B., C., D. prefix if present
            answer_text = re.sub(r'^[A-D]\.\s*', '', answer_text)
            answers.append(answer_text)
        else:
            # Not an answer line, break
            break
        
        i += 1
    
    if len(answers) != 4 or correct_idx == -1:
        print(f"Warning: Question skipped or incomplete: {question[:50]}...")
        return None, i
    
    return {
        'question': question,
        'answers': answers,
        'correct': correct_idx
    }, i

def generate_answer_code(correct_idx):
    """Generate 4-digit binary code for answer (1000, 0100, 0010, 0001)."""
    code = ['0'] * 4
    code[correct_idx] = '1'
    return ''.join(code)

def escape_csv_field(field):
    """Escape field for CSV - wrap in quotes if contains semicolon or newline."""
    field = field.replace('\n', ' ').replace('\r', ' ')
    if ';' in field or '"' in field:
        field = field.replace('"', '""')
        field = f'"{field}"'
    return field

def main():
    # Read the markdown file
    with open('Metodologia.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    questions_data = []
    i = 0
    
    while i < len(lines):
        result, new_i = parse_question_block(lines, i)
        if result:
            questions_data.append(result)
            i = new_i
        else:
            i += 1
    
    print(f"Parsed {len(questions_data)} questions")
    
    # Generate CSV
    csv_lines = []
    
    for q_data in questions_data:
        # Keep question in Italian (no translation)
        question_it = q_data['question']
        
        # Get answers (already in Italian)
        q1 = q_data['answers'][0]
        q2 = q_data['answers'][1]
        q3 = q_data['answers'][2]
        q4 = q_data['answers'][3]
        q5 = ""  # Empty placeholder
        
        # Generate answer code
        answer_code = generate_answer_code(q_data['correct'])
        
        # Build CSV line with semicolon separator
        fields = [
            question_it,
            q1,
            q2,
            q3,
            q4,
            q5,
            answer_code
        ]
        
        # Escape fields
        escaped_fields = [escape_csv_field(f) for f in fields]
        csv_line = ';'.join(escaped_fields)
        csv_lines.append(csv_line)
    
    # Write output
    output_file = 'Metodologia_anki.csv'
    with open(output_file, 'w', encoding='utf-8') as f:
        # No header as requested
        f.write('\n'.join(csv_lines))
    
    print(f"Output written to {output_file}")
    print(f"Total questions: {len(csv_lines)}")
    
    # Print first few lines as preview
    print("\n--- Preview (first 3 questions) ---")
    for line in csv_lines[:3]:
        print(line[:200] + "..." if len(line) > 200 else line)

if __name__ == '__main__':
    main()
