#!/usr/bin/env bash
set -e
set -x

echo "Checking wheel file"
wheel_man_files=$(unzip -l build/dist/SCons-*-py3-none-any.whl | grep -e '[a-z].1$' | tee /dev/stderr | wc -l)
echo "Number of manpage files: $wheel_man_files"

echo "Checking tgz sdist package"
tgz_man_files=$(tar tvfz build/dist/SCons-*.tar.gz | grep -e '[a-z].1$' | tee /dev/stderr | wc -l)

echo "Checking zip sdist package"
zip_man_files=$(unzip -l build/dist/SCons-*.zip | grep -e '[a-z].1$' | tee /dev/stderr | wc -l)

if [[ $wheel_man_files =~ /\\s+4/ ]]; then
   echo "Manpages not in wheel"
   exit 1
fi