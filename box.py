#!/usr/bin/env python

""" 
Christopher Bradshaw												27/12/13
box.py

Contains functions to deal with the box api
"""

# access_token is an access token. . .
# typ must always be "files" or "folders" - specifies which part of the API to use

import requests
import json
import tmp
import sys
import time
import os

# Given the parent id_num and the directory, dirs, we are looking for in that dir
# Return the box id of that dir if it exists, 0 otherwise
def backup_loc(access_token, dirs, id_num):
	
	# Home address
	uri = "https://api.box.com/2.0/folders/" + id_num 
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	r = requests.get(uri, headers = payload)
	
	data = r.json()["item_collection"]["entries"]

	for i in data:
		if i["name"] == dirs:
			return(i["id"])
	
	return(0)

# Given a file_num, returns the json encoded info about that file/folder
# basically 'ls' when typ = 'folders'
def file_info(access_token, file_num, typ):
	uri = "https://api.box.com/2.0/" + typ + "/" + file_num
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	r = requests.get(uri, headers = payload)
	return(r.json())

# Given the folder name and parent box id, creates that folder and returns the
# json encoded info
def box_mkdir(access_token, name, parent_num):
	uri = "https://api.box.com/2.0/folders"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	payload2 = {"name": name, "parent": {"id": str(parent_num)}}
	r = requests.post(uri, headers=payload, data=json.dumps(payload2))
	return(r.json())

# Given the box parent id and the local file, uploads the file and returns
# a json encoded box file object
def upload_file(access_token, parent, local_file):
	uri = "https://upload.box.com/api/2.0/files/content"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	payload2 = {"parent_id": str(parent)} 
	files = {'file': (local_file, open(local_file, 'rb'))}
	r = requests.post(uri, headers=payload, files=files, data=payload2)
	return(r.json())

# Given the box parent id, the local files name and its last modification time
# determines whether the file is to be uploaded (1), not uploaded (0) or
# uploaded, overwriting an old version (string file id of file to overwrite)
def to_upload_file(access_token, sname, fname, parent):

	l_time = os.stat(fname).st_mtime # local modification time
	# Check whether file exists on Box servers
	file_num = 0
	for item in parent["item_collection"]["entries"]:
		if item["name"] == sname:
			file_num = item["id"]
			break
	# return 1 if it doesn't
	if not file_num:
		return(1)
	
	# File exists on box, check modification times
	info = file_info(access_token, file_num, "files")

	if local_newer(l_time, info["modified_at"]):
		return(str(info["id"]))
	
	# Else return 0 - nothing to upload
	return(0)

# Given a box dir id and the corresponding local dir, 
# returns 1 if anything in the local directory is newer than the box dir
def to_upload_dir(access_token, fname, dir_num):
	# We know that the folder exists. Check modification times
	l_time = os.stat(fname).st_mtime
	info = file_info(access_token, dir_num, "folders")
	if local_newer(l_time, info["modified_at"]):
		return(1)
	
	return(0)

# returns 1 if local is newer, 0 otherwise
def local_newer(l_time, b_time):
	l_time += int(b_time[-6:-3]) * 60 * 60 # box uses another time zone
	l_time = time.gmtime(l_time)

	nb_time = b_time[0:4] + b_time[5:7] + b_time[8:10] + b_time[11:13] + b_time[14:16] + b_time[17:19]
	nl_time = str(l_time[0]) + ''.join([str(l_time[i]).zfill(2) for i in range(1,6)])
	
	# Check if local version is newer than box. Return 1 if so
	if nb_time < nl_time:
		return(1)
	return(0)
	

# Deletes the file/folder specified by file_id
def box_rm(access_token, file_id, typ):
	uri = "https://api.box.com/2.0/" + typ + "/" + file_id
	if typ == "folders":
		uri = uri + "?recursive=true"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	requests.delete(uri, headers=payload)
