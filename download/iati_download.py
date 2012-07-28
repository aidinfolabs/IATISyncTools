#IATI Downloader
import sys
import urllib
import json
from datetime import date
import os
import hashlib
import string
import types

def registry_fetch(api_endpoint, *parameters): #To return an object full of all the data. Needs to handle query building and 
	query = string.join(parameters,'&')
	url = api_endpoint + 'search/dataset?' + query + '&limit=100&all_fields=1&offset='
	all_fetched = 0
	offset = 0
	dataset_list = []

	while(all_fetched == 0):
		try:
			if debug_level > 4:
				print "Fetching " + url+str(offset)
			api_connection = urllib.urlopen(url + str(offset))
			data = json.loads(api_connection.read())
		except:
			if debug_level > 0:
				print "Error fetching URL or parsing JSON for url"
		try:
			dataset_list = dataset_list + data['results']
			count = data['count']
			offset = offset + 100
			if offset > count:
				all_fetched = 1

		except TypeError:
			all_fetched = 1 # Set all fetched so we exit the process.
			if debug_level > 0:
				print "Failed loading packages with this response from the registry:" + str(data)			

	if debug_level > 3:
		print str(len(dataset_list)) + " total package details fetched"

	return dataset_list
	
def resource_fetch(dataset_list,directory_pattern = 'datasets/$groups',file_pattern='$name.xml'):
	for dataset in dataset_list:
		for resource in dataset['res_url']:
			flat_dataset = flatten_dataset_details(dataset)
			directory = string.Template(directory_pattern).substitute(flat_dataset)
			filename = string.Template(file_pattern).substitute(flat_dataset)
		
			#ToDo: Add lots of error handling and reporting
			check_dir(directory)
  		
			try:
				if debug_level > 3:
					print "Fetching "+ dataset['name'] + " from " + resource + " into " + directory + "/" + filename
				webFile = urllib.urlopen(resource)
				localFile = open(directory + '/' + filename, 'w')
				localFile.write(webFile.read())
				webFile.close()
			except Exception, e:
				print "Fetching "+ dataset['name'] + " from " + resource + "failed. Error: " + e



def flatten_dataset_details(dataset):
	# This function takes the meta-data dictionary and flattens it out, picking the first value from any list, and flatting out extras. This is primarily to make them available for templating functions.
	flattened = dict()
	for key in dataset:
		if key == 'extras':
		 	for extra_key in dataset['extras']:
		 		flattened[extra_key] = dataset['extras'][extra_key]
		elif type(dataset[key]) == types.ListType:

			flattened[key] = str(dataset[key][0])
		else:
			flattened[key] = dataset[key]
	return flattened
	

def check_dir(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except Exception, e:
            print "Directory creation failed:", e
            print "Couldn't create directory " + dir


## Older




def run(directory,groups):
    url = 'http://iatiregistry.org/api'
    import ckanclient
    registry = ckanclient.CkanClient(base_location=url)
    startnow = False
    for pkg_name in registry.package_register_get():
            try:
                 pkg = registry.package_entity_get(pkg_name)
            except Exception, e:
                 print "Error fetching package ",e

            try:
                group = pkg.get('groups').pop()
            except Exception, e:
                group = "Unknown"
            
            #Check if we were passed a list of groups, or if we're 
            if (not groups) or (group in groups):
                for resource in pkg.get('resources', []):
                    try:
                        if(check_file(pkg_name,dir + group + '/',resource.get('hash'))):
                            print "Saving file "+pkg_name
                            save_file(pkg_name, resource.get('url'), dir + group + '/')
                            print "File saved "+pkg_name
                    except Exception, e:
                        print "Failed:", e
                        print "Couldn't find directory"

def save_file(pkg_name, url, dir):
    check_dir(dir)
    webFile = urllib.urlopen(url)
    localFile = open(dir + '/' + pkg_name + '.xml', 'w')
    localFile.write(webFile.read())
    webFile.close()



def check_file(pkg_name,dir,hash):
    try:
        checkfile = open(dir+'/'+pkg_name+'.xml')
        if(hashlib.sha1(checkfile.read()).hexdigest() == hash):
            print "No update to "+pkg_name
            return False
        else:
            print "File changed. Downloading update to " +pkg_name
            return True
    except Exception, e:
        print "New file - creating " + pkg_name
        return True

if __name__ == '__main__':
	global debug_level
	debug_level = 5 # 0 = silent | 1 = error | 3 = warn | 5 = verbose

	import argparse
	parser = argparse.ArgumentParser(description='Download data packages from the IATI Registry')
	parser.add_argument('--filetype', dest='parameter_filetype', type=str, nargs='?', help='The type of file to search for: activity or organisations.')
	parser.add_argument('--publisher', dest='parameter_group', type=str, nargs='?', help='Only fetch files for a particular publisher.')
	parser.add_argument('--country', dest='parameter_country', type=str, nargs='?', help='Only fetch files for a given country or region codes to fetch data for')
	parser.add_argument('--search', dest='search', type=str, nargs='*', help='Any search parameters supported for datasets by the CKAN API (see http://docs.ckan.org/en/latest/api-v2.html). \n In the format parameter=value. E.g verified=yes')
	args = parser.parse_args()

	if(args.parameter_filetype):
		filetype=args.parameter_filetype
	else:
		filetype=''
	if(args.parameter_group):
		groups = 'groups='+args.parameter_group
	else:
		groups = ''
	if(args.parameter_country):
		country = 'country='+args.parameter_country
	else:
		country = ''
	if(args.search):
		search = string.join(args.search,'&')
	else:
		search = ''


	dataset_list = registry_fetch('http://www.iatiregistry.org/api/',filetype,search,groups,country)

	resource_fetch(dataset_list)
    
#    
#    import sys
#    dir="~/iati/data/packages/"
#    dir = os.path.expanduser(dir)
#    check_dir(dir)
#    run(dir,args.groups)
