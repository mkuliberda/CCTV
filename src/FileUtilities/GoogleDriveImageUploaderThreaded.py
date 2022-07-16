from FileUtilities import GoogleDriveGenericUploader
from datetime import datetime, timedelta
from Utilities import secrets
import json
from threading import Thread
import time
from shutil import move


class GoogleDriveImageUploaderThreaded(GoogleDriveGenericUploader.GoogleDriveGenericUploader, Thread):
    def __init__(self, curl_like_object, file_selector, device_verif_filename, bearer_and_perm_tokens_filename, prio, interface=None, verbose=False, subject=None, move_to_path=None):
        GoogleDriveGenericUploader.GoogleDriveGenericUploader.__init__(
            self,
            curl_like_object=curl_like_object,
            file_selector=file_selector,
            device_verif_filename=device_verif_filename,
            bearer_and_perm_tokens_filename=bearer_and_perm_tokens_filename,
            prio=prio,
            interface=interface,
            verbose=verbose,
            subject=subject)
        self._is_running = True
        self._refresh_rate_seconds = 1
        self._prev_image = None
        self._move_to_path = move_to_path
        Thread.__init__(self)
        self.start()


    def update(self, value):
        raise NotImplementedError


    def run(self):
        while self._is_running is True:
            print("GDrive run, upload count: {}".format(self._upload_count))
            if self._is_uploading is not True:
                try:
                    if datetime.now() >= self.access_token["exp_datetime"]:
                        self.get_new_access_token_from_refresh_token(self._bearer_and_perm_tokens_filename)  #TODO: handle exp time 60minutes, refresh token:7days
                except (KeyError, TypeError):
                    self.get_new_access_token_from_refresh_token(self._bearer_and_perm_tokens_filename)

                current_image = self._file_selector.get_file_relative_path()
                if current_image != self._prev_image and current_image is not None:
                    print("GDrive update, image: {} uploading...".format(current_image))
                    self.upload_image(current_image, secrets.get_gdrive_folder_id())
                    self._prev_image = current_image
                    if self._move_to_path is not None:
                        move(current_image, self._move_to_path + current_image.split("/")[-1])
            time.sleep(self._refresh_rate_seconds)

    
    def terminate(self):
        self._is_running = False


    def set_refresh_rate(self, refresh_rate_seconds):
        self._refresh_rate_seconds = refresh_rate_seconds
    

    def __exit__(self, exc_type, exc_value, traceback):
        self.terminate()


    def upload_image(self, file_path, gdrive_folder_id=None, verbose=False, interface=None):
        if self._upload_count <= self._upload_limit or self._upload_limit < 0:
            self.temporary_settings_enter(verbose, interface)

            self._curl.setopt(self._curl.URL, "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart")
            self._curl.setopt(self._curl.FOLLOWLOCATION, True)
            self._curl.setopt(self._curl.HTTPHEADER, ["Authorization: Bearer " + self.access_token["access_token"]])
            filedata = (self._curl.FORM_FILE, file_path,  self._curl.FORM_CONTENTTYPE, 'image/jpeg',)
            if gdrive_folder_id is not None:
                meta = {"name": file_path.split("/")[-1], "parents": [gdrive_folder_id]}
            else:
                meta = {"name": file_path.split("/")[-1]}
            metadata = (self._curl.FORM_CONTENTS, json.dumps(meta), self._curl.FORM_CONTENTTYPE, 'application/json')
            post_message = [ ('metadata', metadata), ('file', filedata),]
            self._curl.setopt(self._curl.HTTPPOST, post_message)
            self._is_uploading = True
            print(self._curl.perform_rs()) #perform_rs()
            #TODO: check success or fail print(self._curl.perform_rs())
            self._upload_count += 1 #TODO: check success and then increase count
            self._is_uploading = False
            self.temporary_settings_exit(verbose, interface)

        return

