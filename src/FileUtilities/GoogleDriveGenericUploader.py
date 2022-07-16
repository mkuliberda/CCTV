from Observer import observer_abc as AbsObserver
from PriorityManager import SimplePriorityManager as PrioMgr
from FileUtilities import AbstractUploader as AbsUploader
from Utilities import secrets
import json
from urllib.parse import urlencode
from datetime import datetime, timedelta

BEARER_AND_PERM_TOKENS_JSON1 = "bearer_and_perm_tokens1.json"
DEVICE_VERIF_JSON1 = "device_verif1.json"


class GoogleDriveGenericUploader(AbsUploader.AbstractUploader, AbsObserver.AbstractObserver, PrioMgr.SimplePriorityManager):
    def __init__(self, curl_like_object, file_selector, device_verif_filename,
     bearer_and_perm_tokens_filename, prio, interface=None, verbose=False, subject=None):
        PrioMgr.SimplePriorityManager.__init__(self)
        self.set_priority(prio)
        self._subject = subject
        self._device_verif_filename = device_verif_filename
        self._bearer_and_perm_tokens_filename = bearer_and_perm_tokens_filename
        self._is_uploading = False
        self._file_selector = file_selector
        self._curl = curl_like_object
        self._perm_interface = None
        self._interface = None
        self._perm_verbose = None
        self._verbose = None
        self.client_id = secrets.get_gdrive_client_id()
        self.client_secret = secrets.get_gdrive_client_secret()
        self.device_verif = None
        self.access_token = None
        self._upload_limit = -1
        self._upload_count = 0
        self.set_interface(interface)
        self.set_verbose_mode(verbose)

        if subject is not None:
            self._subject.attach(self)
        AbsUploader.AbstractUploader.__init__(self)


    def __exit__(self, exc_type, exc_value, traceback):
        if self._subject is not None:
            self._subject.detach(self)
        self._curl.close()

    
    def get_uploading_state(self):
        return self._is_uploading


    def update(self, value):
        raise NotImplementedError

    def set_interface(self, interface):
        if self._interface != interface and interface is not None:
            self._interface = interface
            self._curl.setopt(self._curl.INTERFACE, self._interface)


    def reset_interface(self):
        self._curl.unsetopt(self._curl.INTERFACE)


    def set_verbose_mode(self, verbose):
        if self._verbose != verbose:
            self._verbose = verbose
            self._curl.setopt(self._curl.VERBOSE, self._verbose)


    def set_upload_limit(self, upload_limit):
        self._upload_limit = upload_limit


    def temporary_settings_enter(self, verbose, interface):
        self._perm_verbose = self._verbose
        self.set_verbose_mode(verbose)
        self._perm_interface = self._interface
        self.set_interface(interface)


    def temporary_settings_exit(self, verbose, interface):
        self.set_interface(self._perm_interface)
        self.set_verbose_mode(self._perm_verbose)


    def verify_device(self, verbose=False, interface=None):
        self.temporary_settings_enter(verbose, interface)

        self._curl.setopt(self._curl.URL, 'https://oauth2.googleapis.com/device/code')
        self._curl.setopt(self._curl.POSTFIELDS,"client_id=" + secrets.get_gdrive_client_id() + "&scope=https://www.googleapis.com/auth/drive.file")
        self.device_verif = json.loads(self._curl.perform_rs())

        self.temporary_settings_exit(verbose, interface)
        return json.dumps(self.device_verif)


    def get_bearer_code(self, device_verif_json_file, verbose=False, interface=None):
        self.temporary_settings_enter(verbose, interface)

        try:
            with open(device_verif_json_file, "r") as infile:
                json_object = json.load(infile)
        except FileNotFoundError:
            with open(device_verif_json_file, "w") as outfile:
                json_object = self.verify_device(verbose, interface)
                outfile.write(json_object)

        self._curl.setopt(self._curl.URL, 'https://accounts.google.com/o/oauth2/token')
        post_data = {
            "client_id": self.client_id, 
            "client_secret": self.client_secret,
            "device_code":  self.device_verif["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
            }
        postfields = urlencode(post_data)
        self._curl.setopt(self._curl.POSTFIELDS, postfields)
        print("Authorize device with user_code via https://www.google.com/device and hit enter, user_code is:", json_object['user_code'])
        input()
        self.access_token = json.loads(self._curl.perform_rs())

        self.temporary_settings_exit(verbose, interface)
        return json.dumps(self.access_token)


    def get_new_access_token_from_refresh_token(self, bearer_and_perm_tokens_json_file, verbose=False, interface=None):
        self.temporary_settings_enter(verbose, interface)
        json_object = None
        try:
            with open(bearer_and_perm_tokens_json_file, "r") as infile:
                json_object = json.load(infile)
        except FileNotFoundError:
            print(bearer_and_perm_tokens_json_file + " file not found, trying to obtain...")
            self.first_run(self._device_verif_filename, bearer_and_perm_tokens_json_file)
            with open(bearer_and_perm_tokens_json_file, "r") as infile:
                json_object = json.load(infile)

        self._curl.setopt(self._curl.URL, "https://accounts.google.com/o/oauth2/token")
        post_data = {
            "client_id": self.client_id, 
            "client_secret": self.client_secret,
            "refresh_token":  json_object["refresh_token"],
            "grant_type": "refresh_token"
            }
        postfields = urlencode(post_data)
        self._curl.setopt(self._curl.POSTFIELDS, postfields)
        self.access_token = json.loads(self._curl.perform_rs())
        self.access_token["exp_datetime"] = datetime.now() + timedelta(seconds=self.access_token["expires_in"])

        self.temporary_settings_exit(verbose, interface)


    def first_run(self, device_verif_json_file, bearer_and_perm_tokens_json_file, verbose=False, interface=None):

        with open(device_verif_json_file, "w") as outfile:
            outfile.write(self.verify_device(verbose, interface))

        with open(bearer_and_perm_tokens_json_file, "w") as outfile:
            outfile.write(self.get_bearer_code(device_verif_json_file, verbose, interface))
        

