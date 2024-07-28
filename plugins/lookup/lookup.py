from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: file
  author: fwi
  version_added: "0.2"
  short_description: Asks for keepass password and caches result for execution session
  description:
      - This lookup returns either a username or password retrieved from a keepass kdbx file
  examples:
    - "{{ lookup('keepass', 'username') }}"
    - "{{ lookup('keepass', 'password') }}"
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from tkinter import *
from tkinter.ttk import *
from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError
from ansible.utils.display import Display
import re

display = Display()

def find_entries_with_field(kp, field_name, field_value):
    # List to hold the entries that match the criteria
    matching_entries = []

    # Iterate through all entries in the KeePass database
    for entry in kp.entries:
        # Check if the entry has the specific field and if its value matches
        if field_name in entry.custom_properties and field_value in entry.custom_properties[field_name]:
            # Handle multiple lines in the field
            for entryVal in entry.custom_properties[field_name].split():
                if entryVal == field_value:
                    matching_entries.append(entry)

    return matching_entries


def find_entry_with_field(self, field_name, field_value, display):
    matching_entries = []

    for entry in self.kp.entries:
        if field_name in entry.custom_properties and field_value in entry.custom_properties[field_name]:
            for entryVal in entry.custom_properties[field_name].split():
                if entryVal == field_value:
                    matching_entries.append(entry)

    if len(matching_entries) > 1:
        display.error("More than one entry has the field %s matching: %s" % (field_name, field_value))
        for matching_entry in matching_entries:
            display.error("%s: %s" % (matching_entry.title, matching_entry.path))
        raise AnsibleError("Too many matches for %s", field_name)
    elif len(matching_entries) == 1:
        return matching_entries[0]

    return None

class LookupModule(LookupBase):
  kp = None

  def run(self, terms, variables=None, **kwargs):

    # Require username or password term in the lookup
    if terms[0] != "username" and terms[0] != "password":
        raise AnsibleError("KeePass: term username or password is required.")

    runtype = terms[0]

    vars = getattr(self._templar, '_available_variables', {})
    host = vars['inventory_hostname']

    # Check if there is a second value, and it's actually has someting, assumts it's a new hostname to pull credentials for.
    if len(terms) == 2 and terms[1]:
        host = terms[1]
        display.v("Keepass Host overwritten to: " + host)


    cache_identifier = host + "|" + runtype
    cached_data = self._get_cached_data(variables, cache_identifier)

    if cached_data is not None:
        display.debug("Using cached %s entry for %s" % (runtype, host))
        return [cached_data]

    # Path to your KeePass database file
    kdbx_file = vars['keepass_dbx']
    password = vars['keepass_psw']

    if self.kp == None:
        self.kp = PyKeePass(kdbx_file, password=password)


    host_field = 'host'
    domain_field = 'domain'

    domain = re.sub(r'^[^.]+\.', '', host)


    result = find_entry_with_field(self, host_field, host, display)
    if result is None:
        result = find_entry_with_field(self, domain_field, domain, display)

    if result is None:
        raise AnsibleError("KeePass: Could not locate credentials for %s" % host)

    # Set cache
    self._set_cached_data(variables, cache_identifier, self._get_result_property(runtype, result))
    return [self._get_result_property(runtype, result)]


  def _get_result_property(self, runtype, result):
        if runtype == "username":
            return result.username
        elif runtype == "password":
            return result.password

  def _get_cached_data(self, variables, key):
      return variables.get(key)

  def _set_cached_data(self, variables, key, value):
      variables[key] = value
