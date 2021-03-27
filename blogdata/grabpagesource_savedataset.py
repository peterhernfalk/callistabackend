import re
import shutil
import ssl
import urllib.request

downloadPagecontents = True
debug = True
blogpagefile = "downloaded_blogpage.txt"
blogdataset = "blogdata_links.txt"
blogdataset_titles = "blogdata_titles.txt"
blogdataset_shorttitles = "blogdata_shorttitles.txt"


if (downloadPagecontents == True):
    # Backup files before download and replace
    shutil.copy("./"+blogpagefile, "./backup/"+blogpagefile)
    shutil.copy("./"+blogdataset, "./backup/"+blogdataset)
    shutil.copy("./"+blogdataset_titles, "./backup/"+blogdataset_titles)
    shutil.copy("./"+blogdataset_shorttitles, "./backup/"+blogdataset_shorttitles)

    # Get a copy of the page that lists all the blogs
    url = "https://callistaenterprise.se/blogg/arkiv/"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    html = urllib.request.urlopen(url, context=ctx).read()

    # Save the page contents to a text file
    f = open(blogpagefile,"wb")
    f.write(html)
    f.close()

# Read the text file into a variable
f = open(blogpagefile,"r")
pagecontents = f.readlines()
f.close()
if (debug == True):
    print("blogpagefile: " + str(len(pagecontents)))

# https://stackoverflow.com/questions/14840310/python-using-re-module-to-parse-an-imported-text-file
# Remove unwanted lines from the text file. Keep lines containing <a href= or ce-presentation-tag
new_file = []
pattern = '^.*a href="/blogg.*$'
#pattern = '^.*a href="/blogg.* | .*ce-presentation-tag.*$'     # BUGG: kapar långa a href-strängar
#pattern = '^.*ce-presentation-tag.* | .<a href="/blogg.*$'
#pattern = '^.(?:*<a href="/blogg.* | *ce-presentation-tag.*)$'
isFirstLine = True
for line in pagecontents:
    match = re.search(pattern, line)
    #previous = ""
    if match:
        if (str(match).find("<li>") < 0) \
                and (str(match).find("h2") < 0)\
                and (str(match).find("tel") < 0)\
                and (str(match).find("twitter") < 0):
            trimmedmatch = str(match.group()).lstrip(' ')
            trimmedmatch = trimmedmatch.replace('<a href="/blogg', '<a href="https://callistaenterprise.se/blogg')
            trimmedmatch = trimmedmatch.replace('/">', '/" target=\'_blank\'>')
            #trimmedmatch = trimmedmatch.replace('</a>', ' </a>')
            if (len(trimmedmatch) > 0):
                if (isFirstLine == True):
                    new_line = trimmedmatch
                    isFirstLine = False
                else:
                    new_line = '\n' + trimmedmatch
                new_file.append(new_line)

            """ 2do
            if (len(new_file) > 0) and (str(match).find("ce-presentation-tag") >= 0):
                #new_file[-1].
                #print(new_file[-1])
                previous += "," + trimmedmatch
                new_line = previous + '\n'
            else:
                new_line = trimmedmatch + '\n'
                new_file.append(new_line)
            previous = trimmedmatch"""

with open(blogdataset, 'w') as f:
    f.seek(0)  # go to start of file
    f.writelines(new_file)
    f.close()

# Append related lines, separated by comma, creating a csv data set

# Save the result in a csv file
#f = open(blogdataset,"w")
#f.write(xxxx)
#f.close()

if (debug == True):
    f = open(blogdataset, "r")
    blogdatacontents = f.readlines()
    f.close()
    print("blogdataset: " + str(len(blogdatacontents)))


#######################################################
#######################################################
# Remove contents that should not be searchable from the file containing blog titles
f = open(blogdataset, "r")
blogdatacontents = f.readlines()
f.close()


new_file_titles = []
for line in blogdatacontents:
    line = line.replace('</a>', '')
    line = line.replace('.', '')
    line = line.replace(',', '')
    line = line.replace(':', '')
    line = line.replace('"', '')
    line = line.replace('!', '')
    line = line.replace('?', '')
    line = line.replace('(', '')
    line = line.replace(')', '')
    line = line.replace(' - ', ' ')
    #line = line.replace('a ', ' ')
    line = line.replace(' and ', ' ')
    line = line.replace(' as ', ' ')
    line = line.replace(' att ', ' ')
    line = line.replace(' av ', ' ')
    line = line.replace(' det ', ' ')
    line = line.replace(' dig ', ' ')
    line = line.replace('dsls', 'dsl')
    line = line.replace('DSLs', 'dsl')
    line = line.replace(' du ', ' ')
    line = line.replace(' en ', ' ')
    line = line.replace(' en ', ' ')
    line = line.replace(' ett ', ' ')
    line = line.replace(' for ', ' ')
    line = line.replace(' får ', ' ')
    line = line.replace(' för ', ' ')
    line = line.replace(' ha ', ' ')
    line = line.replace('har ', '')
    line = line.replace(' hos ', ' ')
    line = line.replace(' i ', ' ')
    line = line.replace(' in ', ' ')
    line = line.replace('is ', ' ')
    line = line.replace(' med ', ' ')
    line = line.replace('nu ', '')
    line = line.replace('ny ', '')
    line = line.replace(' och ', ' ')
    line = line.replace(' on ', ' ')
    line = line.replace(' oss ', ' ')
    line = line.replace(' på ', ' ')
    line = line.replace(' så ', ' ')
    line = line.replace(' till ', ' ')
    line = line.replace('the ', '')
    line = line.replace(' to ', ' ')
    line = line.replace(' ur ', ' ')
    line = line.replace('vi ', '')
    line = line.replace('with ', '')
    line = line.replace('äntligen ', '')
    line = line.replace(' är ', ' ')
    line = line.replace('är ', '')
    index = line.find(">")
    line_titles = line[index+1:]
    new_file_titles.append(line_titles)

with open(blogdataset_titles, 'w') as f:
    f.seek(0)  # go to start of file
    f.writelines(new_file_titles)
    f.close()

#########################################

f = open(blogdataset, "r")
blogdatacontents = f.readlines()
f.close()

new_file_shorttitles = []
isFirstLine = True
for line in blogdatacontents:
    shorttitle_start = re.search('\d{4}', line).start() + 11
    shorttitle_end = re.search('/" target(.*)/', line).start()
    temp_line = line[shorttitle_start:shorttitle_end]
    temp_line = temp_line.replace('-', ' ')
    temp_line = temp_line.replace(' a', '')
    temp_line = temp_line.replace(' i ', '')
    temp_line = temp_line.replace(' 1', '')
    index = 0
    if (isFirstLine == True):
        line_shorttitles = temp_line[index:]
        isFirstLine = False
    else:
        line_shorttitles = '\n' + temp_line[index:]
    new_file_shorttitles.append(line_shorttitles)

with open(blogdataset_shorttitles, 'w') as f:
    f.seek(0)  # go to start of file
    f.writelines(new_file_shorttitles)
    f.close()

