import sys, os, fnmatch
from lxml import etree

# Set up key variables
script_path = os.path.dirname(os.path.realpath(__file__))
exec_path = os.curdir

def clean_file(file):
    f = open(file,'r')
    data = f.read()
    f.close
    f = open(file,'w')
    f.write(data.replace('&#xD;','\\n'))
    f.close()

def process_file(file,transform,suffix):           
    clean_file(file)
    
    try:
        xml = etree.parse(file)
        rdf = transform(xml)
        fileName, fileExtension = os.path.splitext(file)
        f = open(fileName + suffix + '.csv','w')
        f.write(str(rdf))
        f.close() 
    except Exception, e:
        print "Error processing file "+ file
        print e

if __name__ == '__main__':
    global debug_level
    debug_level = 3 # 0 = silent | 1 = error | 3 = notices | 5 = verbose
    
    import argparse
    parser = argparse.ArgumentParser(description='Download data packages from the IATI Registry')
    parser.add_argument('--format', dest='parameter_format', type=str, nargs='?', help='The type of file to search for: activity or organisations.')
    
    args = parser.parse_args()


    if(args.parameter_format == 'transactions'):
        filetype= 'iati-transactions-xml-to-csv'
        suffix = '-transaction'
    elif(args.parameter_format == 'simple'):
        filetype= 'simple-activity-listing.xsl'
        suffix = '-simple'
    else:
        filetype= 'iati-activities-xml-to-csv'
        suffix = '-activity'
    
    
    #Create the XSLT transformation function
    xslt = etree.parse(script_path+'/../../../IATI-XSLT/templates/csv/'+filetype+'.xsl')
    transform = etree.XSLT(xslt)
    
    for root, dirs, files in os.walk(exec_path):
      for filename in fnmatch.filter(files, '*.xml'):
          print(os.path.join(root, filename))
          process_file(os.path.join(root, filename),transform,suffix)
    