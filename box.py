#!/usr/bin/env python

""" 
Christopher Bradshaw												27/12/13
box.py

Contains functions to deal with the box api
"""
import requests
import json
import tmp
import sys
import time

# Given:
# an access token
# a string of the name of the directory we are looking for
# a string of the box id that is the parent of dirs
# Returns:
# the string of the box id of dirs
# or int(0) if it does not exist

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

# Given:
# an access token
# a id of the file we are looking for
# Returns:
# the info about file_num
def file_info(access_token, file_num):
	uri = "https://api.box.com/2.0/files/" + file_num
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	r = requests.get(uri, headers = payload)
	
	data = r.json()
	return(data)

def dir_info(access_token, dir_num):
	uri = "https://api.box.com/2.0/folders/" + dir_num
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	r = requests.get(uri, headers = payload)
	
	data = r.json()
	return(data)

	
# Given:
# an access_token
# an string, id number for a box directory
# Returns:
# a json encoded piece of info about the box dir

def box_ls(access_token, id_num):
	
	uri = "https://api.box.com/2.0/folders/" + id_num 
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	r = requests.get(uri, headers = payload)
	data = r.json()
	return(data)



# Given:
# an access token
# a string name, which is the name of the directory we wish to create
# a string parent_num that is the id of the box directory that is the parent
# Returns:
# a folder object from box
def box_mkdir(access_token, name, parent_num):
	uri = "https://api.box.com/2.0/folders"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	payload2 = {"name": name, "parent": {"id": str(parent_num)}}
	r = requests.post(uri, headers=payload, data=json.dumps(payload2))
	return(r.json())

# Given:
# an access token
# a string name, which is the name of the directory we wish to create
# a string parent_num that is the id of the box directory that is the parent
# Returns:
# a file object of the file

def upload_file(access_token, parent, local_file):
	uri = "https://upload.box.com/api/2.0/files/content"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	payload2 = {"parent_id": str(parent)} 
	files = {'file': (local_file, open(local_file, 'rb'))}
	r = requests.post(uri, headers=payload, files=files, data=payload2)
	return(r.json())

# Given
# an access_token
# the name of the local file
# the local file's last modification time
# all the info from the parent
# Returns
# some string if we need to overwrite the box file
# 1 if we can just upload
# 0 if we don't need to upload
def to_upload_file(access_token, name, l_time, parent):

	file_num = 0
	for item in parent["item_collection"]["entries"]:
		if item["name"] == name:
			file_num = item["id"]
			break
	if not file_num:
		return(1)
	
	# File exists on box, check modification times
	info = file_info(access_token, file_num)
	b_time = info["modified_at"]
	l_time += int(b_time[-6:-3]) * 60 * 60 # box uses another time zone
	l_time = time.gmtime(l_time)

	nb_time = b_time[0:4] + b_time[5:7] + b_time[8:10] + b_time[11:13] + b_time[14:16] + b_time[17:19]
	nl_time = str(l_time[0]) + ''.join([str(l_time[i]).zfill(2) for i in range(1,6)])

	if nb_time < nl_time:
		return(str(info["id"]))
	
	return(0)

def to_upload_dir(access_token, name, l_time, parent):




# Given:
# an access_token
# a file_id
# Deletes the file from box
# Returns nothing
def box_rm(access_token, file_id):
	uri = "https://api.box.com/2.0/files/" + file_id
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	requests.delete(uri, headers=payload)

def box_rmdir(access_token, file_id):
	uri = "https://api.box.com/2.0/folders/" + file_id + "?recursive=true"
	payload = {"Authorization": "Bearer " + access_token["access_token"]}
	requests.delete(uri, headers=payload)
