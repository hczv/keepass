from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.vars import BaseVarsPlugin
from tkinter import *
from tkinter.ttk import *
from ansible.utils.display import Display
import tkinter as tk
from tkinter import simpledialog
import os

DOCUMENTATION = """
    name: prompt_keepass_psw
    short_description: Requests keepass master password
    description:
        - Creates a popup gui window requesting keepass master password
        - Vars plugins gets executed all the time, each host and each group and probably more
          This plugins remembers the first entry, and returns the first result for each call.
        - To enable this plugin, add it to vars_plugins_enabled in ansible.cfg
"""

class PasswordPopup(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="").grid(row=0, column=0)
        self.password_entry = tk.Entry(master, show='*', width=30)
        self.title("Keepass master password")
        self.geometry("400x70")
        self.password_entry.grid(row=0, column=1)
        self.password_entry.bind("<Control-a>", self.select_all)
        self.password_entry.bind("<Control-A>", self.select_all)
        self.password_entry.bind("<Command-a>", self.select_all)  # For macOS
        self.password_entry.bind("<Command-A>", self.select_all)  # For macOS

        # Create an OK button and place it to the right of the password entry
        self.ok_button = tk.Button(master, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        self.ok_button.grid(row=0, column=2, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        return self.password_entry

    def apply(self):
        self.result = self.password_entry.get()

    def select_all(self, event=None):
        self.password_entry.select_range(0, 'end')
        self.password_entry.icursor('end')
        return 'break'

display = Display()

class VarsModule(BaseVarsPlugin):
    _cache = {}

    """
    Loads variables for groups and/or hosts
    """

    def get_vars(self, loader, path, entities, tk = tk.Tk()):

        if os.getenv('SKIP_KEEPASS_PROMPT'):
            # Skip loading this plugin
            return {}

        cache_key = 'cached_var'

        cached_data = self._get_cached_data(cache_key)

        if cached_data is not None:
            display.debug('Using cached master_password')
            return cached_data

        display.v("Requesting master password")
        data = self._generate_data(tk)

        self._set_cached_data(cache_key, data)

        tk.destroy()

        return data

    def _get_cached_data(self, key):
        return self._cache.get(key)

    def _set_cached_data(self, key, value):
        self._cache[key] = value

    def _generate_data(self, tk):
        tk.withdraw()
        dialog = PasswordPopup(tk)

        data = {
            'keepass_psw': f"{dialog.result}"
        }
        return data

