#!/bin/bash

rm -rf ansible_collections
ansible-galaxy collection install -p . . --force
cd ansible_collections/hczv/keepass/
# required sinse ansible-test is stupid https://github.com/ansible/ansible/issues/68499
git init .
ansible-test integration -vvv
cd -

