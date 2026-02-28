#!/usr/bin/env python3
"""Edit Quotes Script.

This script reads an input file containing quotes and writes an output file
with corrected punctuation spacing. The Scanner class processes each character
in the file, applying specific rules for whitespace and punctuation to improve
formatting.

Usage:
    wisdom-quotes input.txt output.txt
    python -m wisdom_tree.edit_quotes input.txt output.txt

The script fixes common issues such as extra spacing or missing spaces after punctuation.
"""

import argparse
import sys
from pathlib import Path


class Scanner:
    """Quote file scanner that fixes punctuation spacing."""

    def __init__(self, original_text_path: str, new_text_path: str):
        """Initialize scanner with input and output file paths.

        Args:
            original_text_path: Path to input quotes file
            new_text_path: Path to output file
        """
        self.original_text_path = original_text_path
        self.new_text_path = new_text_path

        # Read the original file
        with open(original_text_path, encoding='utf-8') as f:
            self.source = f.read()

        # Clear and prepare output file
        with open(new_text_path, 'w', encoding='utf-8') as f:
            f.write('')  # Clear the file

        # Open output file for appending
        self.edited_file = open(new_text_path, 'a', encoding='utf-8')

        # Current position in source text
        self.current = 0

        # Punctuation handlers
        self.punctuation = {
            ' ': lambda c: self.whitespace(c),
            '.': lambda c: self.period(c),
            ',': lambda c: self.colon_comma(c),
            ':': lambda c: self.colon_comma(c),
            ';': lambda c: self.misc_punc(c),
        }

    def close(self):
        """Close output file."""
        self.edited_file.close()

    def add_char(self, c: str) -> None:
        """Add a character to the edited quotes file."""
        self.edited_file.write(c)

    def scan_file(self) -> None:
        """Scan the file and fix common punctuation errors."""
        while not self.is_at_end():
            c = self.advance()  # Get the current character
            if c in self.punctuation:  # If whitespace or punctuation
                self.punctuation[c](c)  # Run the logic for that punctuation
            else:  # Otherwise, add it to the edited quotes file
                self.add_char(c)

    def whitespace(self, current_c: str) -> None:
        """Handle whitespace character.

        Only add whitespace if the next character is not whitespace or punctuation.
        This removes extra spaces and spaces before punctuation.
        """
        next_c = self.peek()
        if next_c not in self.punctuation:
            self.add_char(current_c)

    def misc_punc(self, current_c: str) -> None:
        """Add whitespace after punctuation.

        Adds whitespace after punctuation unless followed by:
        - Quotation marks
        - Newlines
        - Closing brackets/parentheses/braces
        - More whitespace
        """
        next_c = self.peek()
        # If there is no whitespace and no special character after this punctuation
        if next_c not in (' ', '\n', '"', "'", ']', ')', '}'):
            self.add_char(current_c)  # Add the current punctuation
            self.add_char(' ')  # And add whitespace
        else:
            self.add_char(current_c)

    def period(self, current_c: str) -> None:
        """Handle period character.

        If next character is also a period (ellipsis), don't add space.
        Otherwise, apply normal punctuation rules.
        """
        next_c = self.peek()
        if next_c == '.':
            self.add_char(current_c)
        else:
            self.misc_punc(current_c)

    def colon_comma(self, current_c: str) -> None:
        """Handle colon and comma characters.

        If next character is a digit (e.g., time 12:30, number 1,234),
        don't add space. Otherwise, apply normal punctuation rules.
        """
        next_c = self.peek()
        if next_c.isdigit():
            self.add_char(current_c)
        else:
            self.misc_punc(current_c)

    def advance(self) -> str:
        """Return the current character and advance position."""
        c = self.source[self.current]
        self.current += 1
        return c

    def peek(self, extra: int = 0) -> str:
        """Peek at the next character without advancing."""
        return self.source[self.current + extra]

    def is_at_end(self) -> bool:
        """Check if we've reached the end of the source text."""
        return self.current >= len(self.source)


def process_quotes(input_path: Path, output_path: Path) -> None:
    """Process quotes file to fix punctuation.

    Args:
        input_path: Path to input quotes file
        output_path: Path to output file
    """
    scanner = Scanner(str(input_path), str(output_path))
    try:
        scanner.scan_file()
    finally:
        scanner.close()


def main() -> int:
    """CLI entry point for quote processing.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description='Fix punctuation spacing in quotes file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wisdom-quotes input.txt output.txt
  python -m wisdom_tree.edit_quotes quotes.txt fixed_quotes.txt

This tool removes extra spaces, adds spaces after punctuation,
and fixes common formatting issues in quote files.
        """,
    )
    parser.add_argument('input', type=Path, help='Input quotes file')
    parser.add_argument('output', type=Path, help='Output file for edited quotes')
    parser.add_argument(
        '--encoding',
        default='utf-8',
        help='File encoding (default: utf-8)',
    )

    args = parser.parse_args()

    # Validate input file exists
    if not args.input.exists():
        print(f'Error: Input file not found: {args.input}', file=sys.stderr)
        return 1

    if not args.input.is_file():
        print(f'Error: Input path is not a file: {args.input}', file=sys.stderr)
        return 1

    # Create output directory if needed
    args.output.parent.mkdir(parents=True, exist_ok=True)

    try:
        print(f'Processing {args.input}...')
        process_quotes(args.input, args.output)
        print(f'✓ Successfully wrote to {args.output}')
        return 0
    except Exception as e:
        print(f'Error processing quotes: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
