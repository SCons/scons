# __COPYRIGHT__
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

from glob import glob
import os.path


def get_local_package_file_list():
    """
    Get list of all files which should be included in scons-local package
    """
    s_files = glob("SCons/**", recursive=True)

    # import pdb; pdb.set_trace()

    non_test = [f for f in s_files if "Tests.py" not in f]
    non_test_non_doc = [f for f in non_test if '.xml' not in f or "SCons/Tool/docbook" in f]
    filtered_list = [f for f in non_test_non_doc if 'pyc' not in f]
    filtered_list = [f for f in filtered_list if '__pycache__' not in f ]
    filtered_list = [f for f in filtered_list if not os.path.isdir(f)]

    # TODO: add scripts

    return filtered_list


def install_local_package_files(env):

    all_local_installed = []
    files = get_local_package_file_list()
    target_dir = '#/build/scons-local/scons-local-$VERSION'
    for f in files:
        all_local_installed.extend(env.Install(os.path.join(target_dir, os.path.dirname(f)),
                                               f))

    return all_local_installed

def create_local_packages(env):

    installed_files = install_local_package_files(env)



