#!/usr/bin/env python
"""
Christopher Bradshaw 												23/10/2013
sync.py
The main files of box sync for linux. Will handle the getting to token, and the
uploading of files. All these functions will be contained in other files.

todo:
"""

SETTINGS = "settings"
BOX_DIR = "SYNC"

import os
import sys
import requests
import json
import glob

import token
import box
import tmp
import local

# Given:
# an access token
# a string of a local directory/file, fname
# the full json info on the parent of dirs
# Does:
# The shit it needs to
def do(access_token, fname, box_parent, hidden, depth, upfiles):
	sname = local.short_name(fname)
	# if fname is a file, upload file and return 0
	if not os.path.isdir(fname) and upfiles:
		# Check if fname exists in box_parent
		# Return 2 to overwrite (local is newer) 1 to upload (no box version) 0 to do nothing
		up = box.to_upload_file(access_token, sname, fname, box_parent)
		if type(up) == str:
			print "upload and overwrite: {0}".format(fname)
			box.box_rm(access_token, up, "files")
			box.upload_file(access_token, box_parent["id"], fname)
		elif up == 1:
			print "just upload: {0}".format(fname)
			box.upload_file(access_token, box_parent["id"], fname)
		else:
			print "don't upload: {0}".format(fname)
		return(0)

	# If fname is a dir, get its box id number (create if doesn't exist)
	# box num is the box directory corresponding to fname
	elif os.path.isdir(fname):
		box_num = box.backup_loc(access_token, sname, box_parent["id"])
		up = 1

		if not box_num:
			print "Creating dir: {0}".format(fname)
			new_dir = box.box_mkdir(access_token, sname, box_parent["id"])
			box_num = new_dir["id"]
		# exists, check if newer. If local is older, don't do anything with files
		# however, you still need to check lower level subdirs
		else:
			print "no need to create dir: {0}".format(fname)
			up = box.to_upload_dir(access_token, fname, box_num)
			if not up:
				print "no files to upload from: {0}".format(fname)
				

		# get stuff in fname
		os.chdir(fname)
		files = local.listdir(hidden)
		# re call do on all this stuff
		dir_info = box.file_info(access_token, box_num, "folders")
		for i in files:
			do(access_token, i, dir_info, hidden, depth-1, up)
			# Now delete stuff out of this dir in  box that has been deleted in local
		for item in dir_info["item_collection"]["entries"]:
			if item["name"] not in files:
				if item["type"] == "file":
					print "deleting file: {0}".format(item["name"])
					box.box_rm(access_token, item["id"], "files")
				else:
					print "deleting dir: {0}".format(item["name"])
					box.box_rm(access_token, item["id"], "folders")
				
		# And go back a directory
		os.chdir('..')
	else:
		print "We are uploading nothing from this dir, {0}".format(fname)


if __name__ == "__main__":

	print "Updating token"
	#access_token = token.login() # This only needs to be run if token expires
	access_token = token.read_old_token()	
	access_token = token.refresh_token(access_token)
	
	# Get list of files/dirs
	f = open(SETTINGS, "r")
	files = [i.rstrip() for i in f.readlines()]

	
	# Search the root box dir for the sync location.
	# Create if does not exist
	sync_loc = box.backup_loc(access_token, BOX_DIR, "0")
	if not sync_loc: 
		print "Creating sync location on Box"
		new_dir = box.box_mkdir(access_token, BOX_DIR, "0")
		sync_loc = new_dir["id"]
	

	dir_info = box.file_info(access_token, sync_loc, "folders")
	for i in files:
		data = i.split(' ')
		hidden = local.dash_h(data)
		depth = local.depth(data)
		if depth == -1:
			print "{0} has a bad deptht. Ignoring...".format(data[0])
			continue

		if not os.path.exists(data[0]):
			print "{0} does not exist. Ignoring...".format(data[0])
			continue
		do(access_token, data[0], dir_info, hidden, depth, 1)
