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
            for entryVal in entry.custom_properties[field_name].split():
                if entryVal == field_value:
                    matching_entries.append(entry)

    return matching_entries

class LookupModule(LookupBase):
  kp = None

  def run(self, terms, variables=None, **kwargs):
    #self.set_options(var_options=variables, direct=kwargs)
    #default = self.get_option('default')
    vars = getattr(self._templar, '_available_variables', {})
    host = vars['inventory_hostname']

    runtype = None

    if terms[0] == "username":
        runtype = "username"
    elif terms[0] == "password":
        runtype = "password"
    else:
        raise AnsibleError("KeePass: term username or password is required.")

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

    result = ['']
    domain_results = find_entries_with_field(self.kp, domain_field, domain)
    if len(domain_results) > 1:
       display.error("More than one entry has the field %s matching: %s" % (domain_field, domain))
       for domain_result in domain_results:
           display.error("%s: %s" % (domain_result.title, domain_result.path))
       raise AnsibleError("Too many matches for %s", domain_field)
    elif len(domain_results) == 1:
        result[0] = domain_results[0]


    host_results = find_entries_with_field(self.kp, host_field, host)
    if len(host_results) > 1:
       display.error("More than one entry has the field %s matching: %s" % (host_field, host))
       for host_result in host_results:
           display.error("%s: %s" % (host_result.title, host_result.path))
       raise AnsibleError("Too many matches for %s", host_field)
    elif len(host_results) == 1:
        result[0] = host_results[0]

    #print("Retrieved %s entry for %s" % (runtype, host))

    if runtype == "username":
        self._set_cached_data(variables, cache_identifier, result[0].username)
        return [result[0].username]
    elif runtype == "password":
        self._set_cached_data(variables, cache_identifier, result[0].password)
        return [result[0].password]

    #return [host_results[0].password]

  def _get_cached_data(self, variables, key):
      return variables.get(key)

  def _set_cached_data(self, variables, key, value):
      variables[key] = value
