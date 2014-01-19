#!/usr/bin/env python
"""
Christopher Bradshaw 												23/10/2013
sync.py
The main files of box sync for linux. Will handle the getting to token, and the
uploading of files. All these functions will be contained in other files.

todo:
	when updating a file, upload to tmp file, then move.
	also something about versions?
	could we use comments to determine where things came from?
"""

SETTINGS = "settings"
BOX_DIR = "SYNC"

import os
import sys
import requests
import json

import token
import box
import local

# Given an access token, a filename (absolute or relative), an id for the box
# folder that is the parent, and a limit to the depth of recursion
# uploads/updates all the things that need to be uploaded/dated
# deletes things on box that have been deleted locally
def do(access_token, fname, box_parent, hidden, depth):

	sname = local.short_name(fname)

	# if fname is a file, upload file (if necessary) and return 0
	if not os.path.isdir(fname):
		# Determine whether to upload and overwrite (> 0), just upload (0), 
		# do nothing (< 0)
		up = box.to_upload_file(access_token, sname, fname, box_parent)
		if up > 0:
			print "upload and overwrite: {0}".format(fname)
			box.box_rm(access_token, str(up), "file")
			box.upload_file(access_token, box_parent["id"], fname)
		elif up == 0:
			print "just upload: {0}".format(fname)
			box.upload_file(access_token, box_parent["id"], fname)
		elif up < 0:
			print "don't upload: {0}".format(fname)

	# if fname is a dir, create dir if needed and re-call do
	elif os.path.isdir(fname):
		
		# Check if dir exists on box. Create if it doesn't
		box_num = box.dir_id(access_token, sname, box_parent["id"])
		if not box_num:
			print "Creating dir: {0}".format(fname)
			box_num = box.box_mkdir(access_token, sname, box_parent["id"])["id"]
		else:
			print "no need to create dir: {0}".format(fname)
		dir_info = box.file_info(access_token, box_num, "folders")

		# cd into fname and ls
		os.chdir(fname)
		files = local.listdir(hidden)

		# re-call do on all this stuff
		for i in files:
			do(access_token, i, dir_info, hidden, depth-1)

		# Now delete stuff out of this dir in box that no longer exists locally
		box.box_cleanup(access_token, dir_info, files):
		# And go back to the parent directory
		os.chdir('..')
				
if __name__ == "__main__":

	print "Updating token"
	# Do this automatically
	#access_token = token.login() # This only needs to be run if token expires
	access_token = token.read_old_token()	
	access_token = token.refresh_token(access_token)
	
	# Read SETTINGS file and get list of things to upload
	f = open(SETTINGS, "r")
	files = [i.rstrip().split(' ') for i in f.readlines()]
	files = local.remove_duplicates(files)
	
	# Search the root box dir for the sync location.
	sync_loc = box.dir_id(access_token, BOX_DIR, "0")
	# Create if does not exist
	if not sync_loc: 
		print "Creating sync location on Box"
		sync_loc = box.box_mkdir(access_token, BOX_DIR, "0")["id"]

	dir_info = box.file_info(access_token, sync_loc, "folders")

	for data in files:
		hidden = local.dash_h(data)
		depth = local.depth(data)
		
		# Check for errors in settings file
		if depth == -1:
			print "{0} has a bad deptht. Ignoring...".format(data[0])
			continue
		if not os.path.exists(data[0]):
			print "{0} does not exist. Ignoring...".format(data[0])
			continue

		# 'do' all the things we need to do.
		do(access_token, data[0], dir_info, hidden, depth)

	# Cleanup the root dir
	# Fix this
	for item in dir_info["item_collection"]["entries"]:
		if item["name"] not in files:
			print "deleting file: {0}".format(item["name"])
			box.box_rm(access_token, item["id"], item["type"])
