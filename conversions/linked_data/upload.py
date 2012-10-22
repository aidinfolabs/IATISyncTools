import sys, os, fnmatch
from HTTP4Store import HTTP4Store
from rdflib.graph import Graph
from rdflib import Literal, BNode, Namespace
from rdflib import RDF, URIRef
import json

# Set up key variables
script_path = os.path.dirname(os.path.realpath(__file__))
exec_path = os.curdir


def process_file(fileName): 
	store = HTTP4Store('http://localhost:8080')
	fileHandle = open(fileName)
	data = fileHandle.read()
	metaFileName, metaFileExtension = os.path.splitext(fileName) 

	try: 
		metaFile = open(metaFileName + '.meta.json','r')
		metaData = json.loads(metaFile.read())

		try:
			graph_name = metaData['ckan_url']	

			try:
				print "Storing data " +  metaData['name']
				response = store.add_graph(graph_name,data,"xml")
				print "Operation complete. Response status " + str(response.status)

				try:
					#Add to the data data here
					metaRDF = Graph()
					metaRDF.bind("dc", "http://purl.org/dc/elements/1.1/")
					DC = Namespace("http://purl.org/dc/elements/1.1/")

					metaGraph =  URIRef("http://iatiregistry.org/")
					metaRDF.add((URIRef(graph_name),DC['license'],Literal(metaData['license'])))
					metaRDF.add((URIRef(graph_name),DC['title'],Literal(metaData['title'])))
					metaRDF.add((URIRef(graph_name),DC['creator'],Literal(metaData['author_email'])))
				
					try:
						metaRDF.add((URIRef(graph_name),DC['publisher'],Literal(metaData['groups'][0])))
					except:
						pass
					
					try:
						print "Storing meta data for " +  metaData['name']
						response = store.append_graph(graph_name,metaRDF.serialize(),"xml")
						print "Metadata operation complete. Response status " + str(response.status)
						print
					except:
						print "Error storing meta data graph."
				except Exception:
					print "Trouble generating metadata graph" 

			except:
				print "Trouble storing data"
		except:
			print "Trouble reading meta data"

	except:
		print "No meta-data found. Linked data upload currently requires meta-data."




for root, dirs, files in os.walk(exec_path):
  for filename in fnmatch.filter(files, '*.rdf'):
      print(os.path.join(root, filename))
      process_file(os.path.join(root, filename))


