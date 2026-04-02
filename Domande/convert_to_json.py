#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert Markdown quiz files to structured JSON format.
Parses markdown questions with format:
- [x] for correct answers
- [ ] for incorrect answers

Output format: JSON array with structured question objects
[
  {
    "question": "...",
    "answers": [
      {"text": "...", "correct": true/false},
      {"text": "...", "correct": true/false},
      {"text": "...", "correct": true/false},
      {"text": "...", "correct": true/false}
    ],
    "correct_index": 0-3
  }
]

Usage: python3 convert_to_json.py
"""

import re
import os
import glob
import json

def parse_question_block(lines, start_idx):
    """Parse a single question block from markdown."""
    i = start_idx
    
    # Skip empty lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    
    if i >= len(lines):
        return None, i
    
    # Check for question header (## Number - Category)
    # Pattern: ## 583 - Metodology or similar
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
            answers.append({"text": answer_text, "correct": True})
        elif line.startswith('- [ ]'):
            answer_text = line[5:].strip()
            # Remove A., B., C., D. prefix if present
            answer_text = re.sub(r'^[A-D]\.\s*', '', answer_text)
            answers.append({"text": answer_text, "correct": False})
        else:
            # Not an answer line, break
            break
        
        i += 1
    
    if len(answers) != 4:
        print(f"  Warning: Question has {len(answers)} answers instead of 4: {question[:50]}...")
        return None, i
    
    if correct_idx == -1:
        print(f"  Warning: No correct answer found for: {question[:50]}...")
        return None, i
    
    return {
        "question": question,
        "answers": answers,
        "correct_index": correct_idx
    }, i

def process_file(input_file):
    """Process a single markdown file and convert to JSON."""
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
    
    # Generate output filename (same name but .json extension)
    base_name = os.path.splitext(input_file)[0]
    output_file = base_name + '.json'
    
    # Write JSON output with nice formatting
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, ensure_ascii=False, indent=2)
    
    print(f"  Output: {output_file} ({len(questions_data)} questions)")
    return output_file

def main():
    # Find all .md files in current directory
    md_files = glob.glob('*.md')
    
    if not md_files:
        print("No .md files found in current directory")
        return
    
    print(f"Found {len(md_files)} markdown files to process:")
    for f in sorted(md_files):
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
