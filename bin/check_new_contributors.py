#!/usr/bin/env python
"""
Script to list contributors since a specified tag and identify first-time contributors.

This script queries the git history to find all contributors since a given tag.
It then checks if any of these contributors have made prior contributions
(based on their email address) before that tag.
"""

import subprocess
import sys
import argparse
from typing import List, Set, Tuple, Dict

def get_git_output(args: List[str]) -> str:
    """Runs a git command and returns its output as a string.

    Args:
        args: A list of strings representing the git command and its arguments.

    Returns:
        The standard output of the command as a string, stripped of leading/trailing whitespace.

    Raises:
        SystemExit: If the git command returns a non-zero exit code.
    """
    try:
        # Run git command and return output as string
        # using errors='replace' to avoid utf-8 decoding issues
        result = subprocess.check_output(args, stderr=subprocess.STDOUT)
        return result.decode('utf-8', errors='replace').strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {' '.join(args)}")
        print(e.output.decode('utf-8', errors='replace'))
        sys.exit(1)

def get_contributors_since(tag: str) -> Set[Tuple[str, str]]:
    """Retrieves a set of contributors who have committed since the specified tag.

    Args:
        tag: The git tag to compare against (e.g., '4.7.0').

    Returns:
        A set of tuples, where each tuple contains (name, email).
    """
    # Get all authors since the tag
    # Format: Name|Email
    cmd = ['git', 'log', f'{tag}..HEAD', '--format=%aN|%aE']
    output = get_git_output(cmd)
    
    contributors = set()
    if output:
        for line in output.split('\n'):
            if line.strip():
                parts = line.split('|')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    email = parts[1].strip()
                    contributors.add((name, email))
    return contributors

def get_prior_emails(tag: str) -> Set[str]:
    """Retrieves a set of email addresses for all contributors prior to the specified tag.

    Args:
        tag: The git tag to look back from.

    Returns:
        A set of lowercased email address strings for all prior contributors.
    """
    # Get all author emails reachable from the tag
    print("Gathering prior contributors (this may take a moment)...")
    cmd = ['git', 'log', tag, '--format=%aE']
    output = get_git_output(cmd)
    
    prior_emails = set()
    if output:
        for line in output.split('\n'):
            if line.strip():
                # Store lowercase email for consistent comparison
                prior_emails.add(line.strip().lower())
    return prior_emails

def main() -> None:
    """Main function to parse arguments and print the contributor report."""
    parser = argparse.ArgumentParser(description="List contributors since a specified tag and identify first-time contributors.")
    parser.add_argument("tag", help="The git tag to start from (e.g., 4.7.0)")
    args = parser.parse_args()

    # Verify tag exists
    try:
        subprocess.check_call(['git', 'rev-parse', args.tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"Error: Tag '{args.tag}' not found.")
        sys.exit(1)

    # Get new contributors
    recent_contributors = get_contributors_since(args.tag)
    if not recent_contributors:
        print(f"No contributors found since {args.tag}.")
        return

    # Get all prior emails
    prior_emails = get_prior_emails(args.tag)
    
    # Prepare data for display with deduplication
    # Map: display_name -> is_new (boolean)
    contributor_status: Dict[str, bool] = {}
    
    for name, email in recent_contributors:
        display_name = name if name else email
        is_new_email = email.lower() not in prior_emails
        
        if display_name not in contributor_status:
            contributor_status[display_name] = is_new_email
        else:
            # If the contributor was previously marked as new, but this email 
            # is NOT new, then the contributor is not new.
            # If they were already marked as not new, they stay not new.
            if contributor_status[display_name] and not is_new_email:
                contributor_status[display_name] = False
    
    # Convert to list for sorting and display
    display_list = [(name, is_new) for name, is_new in contributor_status.items()]
    
    # Sort by display name (case insensitive)
    display_list.sort(key=lambda x: x[0].lower())
    
    # Calculate max length for alignment
    if display_list:
        max_length = max(len(x[0]) for x in display_list)
    else:
        max_length = 0

    print(f"\nContributors since {args.tag}:")
    print("-" * 40)
    
    for display_name, is_new in display_list:
        # Align left with padding
        if is_new:
            print(f"{display_name:<{max_length}}   Made their first contribution")
        else:
            print(f"{display_name}")

if __name__ == "__main__":
    main()