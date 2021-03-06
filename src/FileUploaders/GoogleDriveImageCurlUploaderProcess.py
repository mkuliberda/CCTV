from FileUploaders.GoogleDriveGenericCurlUploader import GoogleDriveGenericCurlUploader
from datetime import datetime, timedelta
from Utilities import secrets
import json
from multiprocessing import Process
from threading import Thread
import time
from shutil import move
import logging
import pycurl


class GoogleDriveImageCurlUploaderProcess(GoogleDriveGenericCurlUploader, Process):
    def __init__(self, file_selector, device_verif_filename, bearer_and_perm_tokens_filename, interface=None, verbose=False, move_to_path=None):
        GoogleDriveGenericCurlUploader.__init__(
            self,
            file_selector=file_selector,
            device_verif_filename=device_verif_filename,
            bearer_and_perm_tokens_filename=bearer_and_perm_tokens_filename,
            prio=0,
            interface=interface,
            verbose=verbose,
            subject=None)
        self._is_running = True
        self._refresh_rate_seconds = 1
        self._move_to_path = move_to_path
        self._timeout = 600
        self._timeout_counter = 0
        self._d_size = 0
        self._downloaded = 0
        self._u_size = 0
        self._uploaded = 0

        Process.__init__(self)
        self.start()


    def update(self, value):
        raise NotImplementedError


    def run(self):
        while self._is_running is True:
            print("                   uploading: {}, upload count: {}, timeout: {}      ".format(self._is_uploading, self._upload_count, self._timeout_counter), end='\r')
            if self._is_uploading is not True:
                try:
                    if datetime.now() >= self.access_token["exp_datetime"]:
                        self.get_new_access_token_from_refresh_token(self._bearer_and_perm_tokens_filename)  #TODO: handle exp time 60minutes, refresh token:7days
                except (KeyError, TypeError) as e:
                    logging.error(e)
                    self.get_new_access_token_from_refresh_token(self._bearer_and_perm_tokens_filename) #TODO: 
                except pycurl.error as e:
                    logging.error(e)

                current_image = self._file_selector.get_file_relative_path()
                if current_image is not None:
                    self._timeout_counter = 0
                    uploading_thread = Thread(target=self.upload_image, args=(current_image, secrets.get_gdrive_folder_id()))
                    uploading_thread.start()
            time.sleep(self._refresh_rate_seconds)

    
    def terminate(self):
        self._is_running = False


    def set_refresh_rate(self, refresh_rate_seconds):
        self._refresh_rate_seconds = refresh_rate_seconds
    

    def progress(self, *data):
        """it receive progress figures from curl, gets called every second"""
        self._d_size, self._downloaded, self._u_size, self._uploaded = data
        self._timeout_counter+=1
        if self._timeout_counter > self._timeout:
            return -1
        # an example to terminate curl: tell curl to abort if the downloaded data exceeded 1024 byte by returning 0 
        #if downloaded >= 1024:
        #    return -1
       

    def upload_image(self, file_path, gdrive_folder_id=None, verbose=False, interface=None):
        if self._upload_count <= self._upload_limit or self._upload_limit < 0:
            try:
                self._is_uploading = True
                logging.info("{} upload start...".format(file_path))
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
                self._curl.setopt(self._curl.NOPROGRESS, 0)  # required to use a progress function
                self._curl.setopt(self._curl.XFERINFOFUNCTION, self.progress) 

                success = False
                if "error" not in self._curl.perform_rs():
                    success = True #TODO: check success or fail
                    if self._move_to_path is not None:
                        move(file_path, self._move_to_path + file_path.split("/")[-1])
                    self._upload_count += 1
                logging.info("{} upload {}".format(file_path, "success" if success is True else "failed"))
                logging.info("d_size:{}, downloaded:{}, u_size:{}, uploaded:{}".format(self._d_size, self._downloaded, self._u_size, self._uploaded))
            except (pycurl.error, FileNotFoundError, TypeError) as e: #TODO: handle network errors
                logging.error(e)
            finally:
                self._is_uploading = False
                self.temporary_settings_exit(verbose, interface)


    def __exit__(self, exc_type, exc_value, traceback):
        self.terminate()
        self._curl.close()
        self.kill()


