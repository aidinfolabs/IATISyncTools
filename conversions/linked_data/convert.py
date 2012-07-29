import sys, os, fnmatch
from lxml import etree

# Set up key variables
script_path = os.path.dirname(os.path.realpath(__file__))
exec_path = os.curdir

#Create the XSLT transformation function
xslt = etree.parse(script_path+'/../../../IATI-XSLT/templates/rdf/iati-activities-rdf.xsl')
transform = etree.XSLT(xslt)


def clean_file(file):
    f = open(file,'r')
    data = f.read()
    f.close
    f = open(file,'w')
    f.write(data.replace('&#xD;','\\n'))
    f.close()

def process_file(file):           
    clean_file(file)
    
    try:
        xml = etree.parse(file)
        rdf = transform(xml)
        fileName, fileExtension = os.path.splitext(file)
        f = open(fileName + '.rdf','w')
        f.write(str(rdf))
        f.close() 
    except Exception, e:
        print "Error processing file "+ file
        print e

for root, dirs, files in os.walk(exec_path):
  for filename in fnmatch.filter(files, '*.xml'):
      print(os.path.join(root, filename))
      process_file(os.path.join(root, filename))
