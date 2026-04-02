#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert Markdown quiz files to Anki TXT format (CSV format inside, but .txt extension).
Parses markdown questions with format:
- [x] for correct answers
- [ ] for incorrect answers

Output format (semicolon separated):
Field 1 (Question in Italian); Q1; Q2; Q3; Q4; Q5 (empty); Answer (1000, 0100, 0010, 0001)

Usage: python3 convert_all_to_anki.py
"""

import re
import os
import glob

def parse_question_block(lines, start_idx):
    """Parse a single question block from markdown."""
    i = start_idx
    
    # Skip empty lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    
    if i >= len(lines):
        return None, i
    
    # Check for question header (## Number - Category)
    # Pattern: ## 583 - Metodologia or similar
    header_match = re.match(r'^##\s*\d+\s*-\s*\w+', lines[i])
    if not header_match:
        return None, i + 1
    
    i += 1
    
    # Skip empty lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    
    if i >= len(lines):
        return None, i
    
    # Get question text (should be in bold **...**)
    question_line = lines[i].strip()
    question_match = re.match(r'^\*\*(.+?)\*\*$', question_line)
    if question_match:
        question = question_match.group(1)
    else:
        # Handle case where question might be plain text or mixed
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
        print(f"  Warning: Incomplete question: {question[:50]}...")
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

def process_file(input_file):
    """Process a single markdown file and convert to Anki TXT format."""
    print(f"\nProcessing: {input_file}")
    
    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
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
    
    if len(questions_data) == 0:
        print(f"  No questions found in {input_file}")
        return None
    
    print(f"  Parsed {len(questions_data)} questions")
    
    # Generate CSV content
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
    
    # Generate output filename (same name but .txt extension)
    base_name = os.path.splitext(input_file)[0]
    output_file = base_name + '_anki.txt'
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        # No header as requested
        f.write('\n'.join(csv_lines))
    
    print(f"  Output: {output_file} ({len(csv_lines)} questions)")
    return output_file

def main():
    # Find all .md files in current directory
    md_files = glob.glob('*.md')
    
    if not md_files:
        print("No .md files found in current directory")
        return
    
    print(f"Found {len(md_files)} markdown files to process:")
    for f in md_files:
        print(f"  - {f}")
    
    processed = []
    for md_file in sorted(md_files):
        result = process_file(md_file)
        if result:
            processed.append(result)
    
    print(f"\n{'='*50}")
    print(f"Completed! Processed {len(processed)} files:")
    for f in processed:
        print(f"  - {f}")

if __name__ == '__main__':
    main()
