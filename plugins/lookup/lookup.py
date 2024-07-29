from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: keepass
    description:
        - This plugin allows you to lookup KeePass entries by username or password
        - The plugin will search for entries by url and two custom fields host-field and domain-field
        - Order of search is url, host-field, domain-field, and the first match is returned
    options:
        _terms:
            description:
                - The terms to lookup, either 'username' or 'password'.
            required: True
        host:
            description: The hostname to pull credentials for.
            required: False
            default: inventory_hostname
    examples:
        - "{{ lookup('hczv.keepass.lookup', 'username') }}"
        - "{{ lookup('hczv.keepass.lookup', 'password') }}"
        - "{{ lookup('hczv.keepass.lookup', 'username', 'my-host.example.tld') }}"
        - "{{ lookup('hczv.keepass.lookup', 'password', 'my-host.example.tld') }}"
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from tkinter import *
from tkinter.ttk import *
from pykeepass import PyKeePass
from ansible.utils.display import Display
import re

display = Display()

def find_entry_with_field(self, field_name, field_value, display):
    matching_entries = []

    for entry in self.kp.entries:
        if field_name == "url":
            if entry.url == field_value and (entry.url.startswith("ssh://") or not entry.url.find("://") != -1):
                matching_entries.append(entry)
        elif field_name in entry.custom_properties and field_value in entry.custom_properties[field_name]:
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

def resolve_reference(kp, reference):
    # Parse the reference
    match = re.match(r'\{REF:([A-Z])@I:([0-9A-F]+)\}', reference)
    if not match:
        raise ValueError("Invalid reference format")

    field, uuid = match.groups()

    # Convert the UUID to the expected format (hyphenated)
    uuid = '-'.join([uuid[:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:]])

    # Find the entry by UUID
    ref_entry = kp.find_entries(uuid, first=True)
    if not ref_entry:
        raise ValueError("Referenced entry not found")

    # Retrieve the corresponding field
    if field == 'U':
        return ref_entry.username
    elif field == 'P':
        return ref_entry.password
    else:
        raise ValueError("Unknown field type")


class LookupModule(LookupBase):
  kp = None

  def run(self, terms, variables=None, **kwargs):

    # Require username or password term in the lookup
    if terms[0] != "username" and terms[0] != "password":
        raise AnsibleError("KeePass term username or password is required.")

    runtype = terms[0]

    vars = getattr(self._templar, '_available_variables', {})
    host = vars['inventory_hostname']

    # Check if there is a second value, and it's actually has someting, assumts it's a new hostname to pull credentials for.
    if len(terms) == 2 and terms[1]:
        host = terms[1]
        display.v("KeePass Host overwritten to: " + host)


    cache_identifier = host + "|" + runtype
    cached_data = self._get_cached_data(variables, cache_identifier)

    if cached_data is not None:
        display.v("Using cached %s entry for %s" % (runtype, host))
        return [cached_data]
    #else:
    #    display.v("No cached %s entry for %s" % (runtype, host))

    # Path to your KeePass database file
    kdbx_file = vars['keepass_dbx']
    password = vars['keepass_psw']

    if self.kp == None:
        self.kp = PyKeePass(kdbx_file, password=password)


    host_field = 'host'
    domain_field = 'domain'

    domain = re.sub(r'^[^.]+\.', '', host)

    entry = find_entry_with_field(self, "url", host, display)
    if entry is None:
        entry = find_entry_with_field(self, host_field, host, display)
    if entry is None:
        entry = find_entry_with_field(self, domain_field, domain, display)

    if entry is None:
        raise AnsibleError("KeePass: Could not locate credentials for %s" % host)

    # Set cache
    display.vvv("Using keepass entry %s for %s" % (entry.path, host))
    result = self._get_result_value(entry, runtype)

    self._set_cached_data(variables, cache_identifier, result)
    return [result]


  def _get_result_value(self, entry, runtype):
        result = None
        if runtype == "username":
            result = entry.username
        elif runtype == "password":
            result = entry.password

        if result is None or result == "":
            display.error("KeePass entry %s has empty %s field" % (entry.path, runtype))
            #raise AnsibleError("KeePass entry %s has empty %s field" % (entry.path, runtype))
        elif result.startswith("{REF:"):
            result = resolve_reference(self.kp, result)

        return result

  def _get_cached_data(self, variables, key):
      return variables.get(key)

  def _set_cached_data(self, variables, key, value):
      variables[key] = value

