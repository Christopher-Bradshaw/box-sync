#!/usr/bin/env python

""" 
Christopher Bradshaw												27/12/13
box.py

Contains functions to deal with the box api

todo:
	Error checking is basic.
"""

# access_token is an access token. . .
# typ must always be "files" or "folders" - specifies which part of the API to use

import requests
import json
import tmp
import sys
import time
import os
from hashlib import sha1

# Given the parent id_num and the directory, dirs, we are looking for in that dir
# Return the box id of that dir if it exists, 0 otherwise
def dir_id(access_token, dirs, id_num):
	
	uri = "https://api.box.com/2.0/folders/" + id_num 
	payload = {"Authorization": "Bearer " + access_token["access_token"]}

	while 1:
		r = requests.get(uri, headers = payload)
		if r.status_code == 200:
			break

	data = r.json()

	for item in data["item_collection"]["entries"]:
		if item["name"] == dirs:
			return(item["id"])
	return(0)

# Given a file_num, returns the json encoded info about that file/folder
# basically 'ls' when typ = 'folders'
def file_info(access_token, file_num, typ):
	uri = "https://api.box.com/2.0/" + typ + "/" + file_num
	payload = {"Authorization": "Bearer " + access_token["access_token"]}

	while 1:
		r = requests.get(uri, headers = payload)
		if r.status_code == 200:
			break
	
	return(r.json())

# Given the folder name and parent box id, creates that folder and returns the
# json encoded info
def box_mkdir(access_token, name, parent_num):
	uri = "https://api.box.com/2.0/folders"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	payload2 = {"name": name, "parent": {"id": str(parent_num)}}

	while 1:
		r = requests.post(uri, headers=payload, data=json.dumps(payload2))
		if r.status_code == 201:
			break
	
	return(r.json())

# Given the box parent id and the local file, uploads the file and returns
# a json encoded box file object
def upload_file(access_token, parent, local_file):
	uri = "https://upload.box.com/api/2.0/files/content"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	payload2 = {"parent_id": str(parent)} 
	files = {'file': (local_file, open(local_file, 'rb'))}

	while 1:
		r = requests.post(uri, headers=payload, files=files, data=payload2)
		if r.status_code == 201:
			break
	
	return(r.json())

# Given the box parent json data, the local files name, and sname.
# determines whether the file is to be uploaded (0), not uploaded (< 0) or
# uploaded, overwriting an old version (> 0 int file id of file to overwrite)
def to_upload_file(access_token, sname, fname, parent):

	# Check whether file exists on Box servers. Return 0 (upload) if it doesn't
	for item in parent["item_collection"]["entries"]:
		if item["name"] == sname:
			break # exists!
	else:
		return(0)
	
	# File exists on box check hash
	l_hash = sha1(open(fname).read()).hexdigest()

	# If hashes are the same, the file has not changed. No upload
	if item["sha1"] == l_hash:
		return(-1)
	# Different = upload. The assumption made here is that different implies 
	# older. This is not true if we have multiple devices...
	return(item["id"])

# Deletes from the box dir specified by dir_info anything that is not also in
# files
def box_cleanup(access_token, dir_info, files):
	for item in dir_info["item_collection"]["entries"]:
		if item["name"] not in files:
			print "deleting file: {0}".format(item["name"])
			box_rm(access_token, item["id"], item["type"] + 's')


# Deletes the file/folder specified by file_id
def box_rm(access_token, file_id, typ):
	uri = "https://api.box.com/2.0/" + typ + "/" + file_id
	if typ == "folders":
		uri = uri + "?recursive=true"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	while 1:
		r = requests.delete(uri, headers=payload)
		if r.status_code == 204:
			break
