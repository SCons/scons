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
"""

XML_OLD_HEADER = """<!--

  __COPYRIGHT__

  Permission is hereby granted, free of charge, to any person obtaining
  a copy of this software and associated documentation files (the
  "Software"), to deal in the Software without restriction, including
  without limitation the rights to use, copy, modify, merge, publish,
  distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to
  the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
  KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-->"""

# This is the intermediate MIT header that might be present in some files
XML_MIT_HEADER = """<!--

  MIT License

  Copyright The SCons Foundation
  Permission is hereby granted, free of charge, to any person obtaining
  a copy of this software and associated documentation files (the
  "Software"), to deal in the Software without restriction, including
  without limitation the rights to use, copy, modify, merge, publish,
  distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to
  the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
  KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-->"""

XML_NEW_HEADER = """<!--
SPDX-FileCopyrightText: Copyright The SCons Foundation (https://scons.org)
SPDX-License-Identifier: MIT
SPDX-FileType: DOCUMENTATION
-->"""

def update_xml_file(file_path):
    try:
        if os.path.getsize(file_path) == 0:
            print(f"Skipping empty file: {file_path}")
            return

        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content

        # Replace either the old __COPYRIGHT__ header or the previous MIT header
        updated_content = content
        if XML_OLD_HEADER in content:
            updated_content = updated_content.replace(XML_OLD_HEADER, XML_NEW_HEADER)
        if XML_MIT_HEADER in content:
            updated_content = updated_content.replace(XML_MIT_HEADER, XML_NEW_HEADER)

        if updated_content != original_content:
            with open(file_path, 'w') as f:
                f.write(updated_content)
            print(f"Updated XML: {file_path}")
        else:
            print(f"No changes: {file_path}")
    except Exception as e:
        print(f"Failed to update XML {file_path}: {e}")

def update_file(file_path, add_shebang=True):
    if file_path.endswith('.xml') or file_path.endswith('.xsl'):
        update_xml_file(file_path)
        return

    # SConstruct and SConscript files are Python but should not have a shebang added
    # (and existing one preserved if present, which is handled by add_shebang=False)
    if os.path.basename(file_path) in ('SConstruct', 'SConscript'):
        add_shebang = False

    try:
        if os.path.getsize(file_path) == 0:
            print(f"Skipping empty file: {file_path}")
            return

        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content

        # Detect and strip Shebang for processing
        file_shebang = ""
        if content.startswith("#!"):
            lines = content.splitlines(keepends=True)
            file_shebang = lines[0]
            content = "".join(lines[1:])

        # Detect existing Docstring at start
        docstring = ""
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

                in_header = False
                lines_to_keep.append(line)
            else:
                lines_to_keep.append(line)

        new_docstring = ""
        if description_comments and not docstring:
            cleaned_lines = []
            for line in description_comments:
                s = line.strip()
                if s.startswith('#'):
                    val = s[1:]
                    if val.startswith(' '):
                        val = val[1:]
                    cleaned_lines.append(val)
                else:
                    cleaned_lines.append("")

            while cleaned_lines and not cleaned_lines[-1]:
                cleaned_lines.pop()

            if cleaned_lines:
                doc_content = "\n".join(cleaned_lines)
                new_docstring = f'"""\n{doc_content}\n"""'

        rest_of_content = "".join(lines_to_keep)

        # Reassemble
        header_to_use = NEW_HEADER.strip()
        final_prefix = ""

        if add_shebang:
            # Use NEW_HEADER as is (it has shebang)
            final_prefix = header_to_use + "\n"
        else:
            # Use file's original shebang (if any) + NEW_HEADER without its shebang
            header_lines = header_to_use.splitlines(keepends=True)
            if header_lines and header_lines[0].startswith("#!"):
                header_to_use = "".join(header_lines[1:]).lstrip()

            if file_shebang:
                final_prefix = file_shebang + header_to_use + "\n"
            else:
                final_prefix = header_to_use + "\n"

        final_content = final_prefix

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
    parser.add_argument("--no-shebang", action="store_false", dest="add_shebang", help="Do not add shebang line to updated files")
    parser.set_defaults(add_shebang=True)
    args = parser.parse_args()

    for path in args.paths:
        if os.path.isfile(path):
            update_file(path, add_shebang=args.add_shebang)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.py') or file.endswith('.xml') or file.endswith('.xsl') or file in ('SConstruct', 'SConscript'):
                        update_file(os.path.join(root, file), add_shebang=args.add_shebang)
        else:
            print(f"Path not found: {path}")

if __name__ == "__main__":
    main()
