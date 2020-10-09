#!/usr/bin/env bash
set -e
set -x

retval=0
expected_man_file_count=3
echo "Checking wheel file"
wheel_man_files=$(unzip -l build/dist/SCons-*-py3-none-any.whl | grep -e '[a-z].1$' | wc -l | xargs)
echo "Number of manpage files: $wheel_man_files"

echo "Checking tgz sdist package"
tgz_man_files=$(tar tvfz build/dist/SCons-*.tar.gz | grep -e '[a-z].1$' | wc -l |xargs)

echo "Checking zip sdist package"
zip_man_files=$(unzip -l build/dist/SCons-*.zip | grep -e '[a-z].1$' | wc -l |xargs)

if [[ $wheel_man_files != $expected_man_file_count ]]; then
   echo "Manpages not in wheel"
   retval=1
fi

if [[ $tgz_man_files != $expected_man_file_count ]]; then
   echo "Manpages not in tgz sdist package"
   retval=2
fi

if [[ $zip_man_files != $expected_man_file_count ]]; then
   echo "Manpages not in zip sdist package"
   retval=3
fi

exit $retval