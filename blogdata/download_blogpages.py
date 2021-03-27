import re
import shutil
import ssl
import urllib.request

debug = True
blogdataset_links = "blogdata_links_extract.txt"
blogdataset_pages = "blogdata_pages.txt"
output_dataset = []


# Get a copy of the page that lists all the blogs
blogdata_links = open(blogdataset_links, 'r').readlines()
for link in blogdata_links:
    url = link
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    html = urllib.request.urlopen(url, context=ctx).read()
    output_dataset.append(html)
print(len(output_dataset))
print(output_dataset)

with open(blogdataset_pages, 'w') as filehandle:
    for listitem in output_dataset:
        filehandle.write('%s\n' % listitem)

#with open('listfile.txt', 'w') as filehandle:
#    for listitem in places:
#        filehandle.write('%s\n' % listitem)

#f = open(blogdataset_pages,"wb")
#f.write(output_dataset)
#f.close()

