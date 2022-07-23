from FileUploaders.GoogleDriveGenericUploader import GoogleDriveGenericUploader
from datetime import datetime, timedelta
from Utilities import secrets
import json
import threading

class GoogleDriveImageUploader(GoogleDriveGenericUploader):
    def __init__(self, curl_like_object, file_selector, device_verif_filename,
     bearer_and_perm_tokens_filename, prio, interface=None, verbose=False, subject=None):
     GoogleDriveGenericUploader.__init__(
        self,
        curl_like_object=curl_like_object,
        file_selector=file_selector,
        device_verif_filename=device_verif_filename,
        bearer_and_perm_tokens_filename=bearer_and_perm_tokens_filename,
        prio=prio,
        interface=interface,
        verbose=verbose,
        subject=subject)
     self._old_value = False
     self._prev_image = None


    def update(self, value):
        #TODO:  maybe implement upload limit?
        if value is True and self._is_uploading is not True:
            try:
                if datetime.now() >= self.access_token["exp_datetime"]:
                    self.get_new_access_token_from_refresh_token(self._bearer_and_perm_tokens_filename)  #TODO: handle exp time 60minutes, refresh token:7days
            except (KeyError, TypeError):
                self.get_new_access_token_from_refresh_token(self._bearer_and_perm_tokens_filename)

            current_image = self._file_selector.get_file_relative_path()
            if current_image != self._prev_image and current_image is not None:
                logging.info("{} uploading...".format(current_image))
                thread = threading.Thread(target=self.upload_image, args=(current_image, secrets.get_gdrive_folder_id(),))
                thread.start()
                self._prev_image = current_image


    def upload_image(self, file_path, gdrive_folder_id=None, verbose=False, interface=None):
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
        self._curl.perform() #perform_rs()
        success = True #TODO: check success or fail print(self._curl.perform_rs())
        logging.info("{} upload {}".format(file_path, "success" if success is True else "failed"))
        self._is_uploading = False
        self.temporary_settings_exit(verbose, interface)

        return success

