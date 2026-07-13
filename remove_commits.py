#!/usr/bin/env python3
import subprocess
import sys

def run_command(cmd):
    """Run a git command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        print(f"Error: {e}")
        return None, 1

def main():
    # Get all commits by Harsh Singhal
    output, code = run_command('git log --all --pretty=format:"%H" --author="Harsh Singhal"')
    
    if code != 0:
        print("Error getting commits")
        return
    
    commits = output.split('\n') if output else []
    print(f"Found {len(commits)} commits by Harsh Singhal")
    
    if not commits or commits[0] == '':
        print("No commits found")
        return
    
    # Get the root commit (oldest)
    root_commit = commits[-1] if commits else None
    print(f"Root commit: {root_commit}")
    
    # Get parent of root commit to start rebase from there
    output, code = run_command(f'git rev-parse {root_commit}^')
    
    if code == 0:
        parent = output
        print(f"Parent commit: {parent}")
        # Interactive rebase from parent, which will let us drop all Harsh Singhal commits
        print(f"Starting interactive rebase from {parent}...")
        subprocess.run(f'git rebase -i {parent}', shell=False)
    else:
        print("This is the first commit in the repository")
        print("Cannot rebase - all commits are by Harsh Singhal")
        sys.exit(1)

if __name__ == "__main__":
    main()
