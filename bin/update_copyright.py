#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import re
import argparse

NEW_HEADER = """#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# \"Software\"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

def update_file(file_path):
    try:
        if os.path.getsize(file_path) == 0:
            print(f"Skipping empty file: {file_path}")
            return

        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content

        # Detect Shebang (preserve original if different, or use one from new header?)
        # The new header includes a shebang. We should probably strip the file's original shebang
        # and rely on the new header's shebang.
        
        if content.startswith("#!"):
            lines = content.splitlines(keepends=True)
            # shebang = lines[0] # Not used currently as we prepend NEW_HEADER
            content = "".join(lines[1:])
        
        # Detect Docstring at start
        docstring = ""
        # Match triple-quoted strings at the very beginning of the remaining content
        match = re.match(r'^\s*("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', content, re.MULTILINE)
        if match:
            docstring = match.group(1)
            content = content[match.end():]

        # Parse lines to identify header block, revision, and potential new docstring comments
        lines = content.splitlines(keepends=True)
        
        in_header = True
        seen_revision = False
        revision_regex = re.compile(r'^__revision__\s*=')
        
        header_comments = []      # To be discarded (Old License)
        description_comments = [] # To be converted to docstring
        lines_to_keep = []        # Code
        
        for line in lines:
            if in_header:
                sline = line.strip()
                if not sline:
                    # Blank line
                    if seen_revision:
                        # Keep blank lines if we are collecting description (paragraph breaks)
                        # but only if we already have some description content to avoid leading newlines
                        if description_comments:
                            description_comments.append(line)
                    continue
                
                if sline.startswith('#'):
                    if seen_revision:
                        description_comments.append(line)
                    else:
                        header_comments.append(line)
                    continue
                
                if revision_regex.match(sline):
                    seen_revision = True
                    continue
                    
                # Hit code or import or something else
                in_header = False
                lines_to_keep.append(line)
            else:
                lines_to_keep.append(line)
                
        # Process description_comments into a docstring if found and no existing docstring
        new_docstring = ""
        if description_comments and not docstring:
            # Clean up comments
            cleaned_lines = []
            for line in description_comments:
                s = line.strip()
                # Remove leading '#'
                if s.startswith('#'):
                    # Remove '#' and optional single following space
                    val = s[1:]
                    if val.startswith(' '):
                        val = val[1:]
                    cleaned_lines.append(val)
                else:
                    # Blank line
                    cleaned_lines.append("")
            
            # Remove trailing blank lines from the description
            while cleaned_lines and not cleaned_lines[-1]:
                cleaned_lines.pop()
                
            if cleaned_lines:
                doc_content = "\n".join(cleaned_lines)
                new_docstring = f'"""\n{doc_content}\n"""'

        rest_of_content = "".join(lines_to_keep)
        
        # Reassemble
        final_content = NEW_HEADER.strip() + "\n"
        
        # Prefer existing docstring if present, otherwise use converted one
        final_doc = docstring if docstring else new_docstring
        
        if final_doc:
            final_content += "\n" + final_doc + "\n"
        
        if rest_of_content:
             final_content += "\n" + rest_of_content.lstrip()
        else:
             final_content += "\n"

        if final_content != original_content:
            with open(file_path, 'w') as f:
                f.write(final_content)
            print(f"Updated: {file_path}")
        else:
            print(f"No changes: {file_path}")

    except Exception as e:
        print(f"Failed to update {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Update copyright headers in files.")
    parser.add_argument("paths", nargs='+', help="Files or directories to update")
    args = parser.parse_args()

    for path in args.paths:
        if os.path.isfile(path):
            update_file(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    # Filter for python files only? 
                    # The prompt didn't strictly say only python files, but the header is python style.
                    # I'll stick to .py files to be safe, or files with python shebang?
                    # Given the context of previous tasks, let's assume .py files.
                    if file.endswith('.py'):
                        update_file(os.path.join(root, file))
        else:
            print(f"Path not found: {path}")

if __name__ == "__main__":
    main()
