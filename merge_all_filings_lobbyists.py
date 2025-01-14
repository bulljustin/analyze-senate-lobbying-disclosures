# Can download files needed from here
# https://www.senate.gov/legislative/Public_Disclosure/database_download.htm

import os
import csv
import xml.etree.ElementTree as ET


# set up function to make list unique and keep order
def unique_list(seq, idfun=None):
  # order preserving
  if idfun is None:
    def idfun(x): return x
  seen = {}
  result = []
  for item in seq:
    marker = idfun(item)
    # in old Python versions:
    # if seen.has_key(marker)
    # but in new ones:
    if marker in seen: continue
    seen[marker] = 1
    result.append(item)
  return result


# set up function to get xml files you want to use
def get_filepaths(directory):
  # got this function from here http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory
  #    This function will generate the file names in a directory
  #    tree by walking the tree either top-down or bottom-up. For each
  #    directory in the tree rooted at directory top (including top itself),
  #    it yields a 3-tuple (dirpath, dirnames, filenames).
  xml_paths = []  # List which will store all of the full filepaths.

  # Walk the tree.
  for root, directories, files in os.walk(directory):
    for filename in files:
      # Join the two strings in order to form the full filepath.
      filepath = os.path.join(root, filename)
      if ".xml" in filepath:
        xml_paths.append(filepath)  # Add it to the list.

  return xml_paths  # Self-explanatory.


# creates list of files to use
xml_paths = get_filepaths("xmls_to_use")

# sets up container for contents of each xml
list_of_xml_reads = []


# sets up function to remove last line of string
# from here
# http://stackoverflow.com/questions/18682965/python-remove-last-line-from-string/18683105#18683105
def remove_last_line_from_string(s):
  return s[:s.rfind('\n')]


# trims header and footer of xml and inserts into container
for xml_path in xml_paths:
  with open(xml_path, "r", encoding="UTF-16") as xml:
    xml_read = xml.read()
    xml_clean_read = xml_read.split("\n", 4)[4];
    xml_clean_read = remove_last_line_from_string(xml_clean_read)
    list_of_xml_reads.append(xml_clean_read)

# adds header and footer to container of xml contents that wraps them all
list_of_xml_reads.insert(0, "<?xml version='1.0' encoding='UTF-16'?>\n<PublicFilings>")
list_of_xml_reads.append("</PublicFilings>")

# joins the list of xml contents into one string that can be parsed as xml
large_xml_contents = "\n".join(list_of_xml_reads)

# parse xml
parser = ET.XMLParser(encoding="UTF-16")
root = ET.fromstring(large_xml_contents, parser=parser)

# create variable for all individual fillings
all_filings = root.findall("./Filing")

# filters filings within root
# for filing in all_filings:
#   # 	# format for filters: IF location in tree DOES NOT EQUAL what we want it to be REMOVE the filing FROM ROOT
#   # 	if filing.attrib["Year"] != "2017":
#   # 		root.remove(filing)
#   # 		continue
#   if filing.attrib["Type"] != "REGISTRATION" and filing.attrib["Type"] != "REGISTRATION AMENDMENT":
#     root.remove(filing)
#     continue
# 	# Because there are multiple issues in one filing, below filter is example of how to filter where at least one of the issues is coded as BANKING or FINANCIAL INSTITUTIONS/INVESTMENTS/SECURITIES
# 	# codes = []
# 	# for issue in filing.findall("Issues/Issue"):
# 	# 	codes.append(issue.attrib["Code"])
# 	# if "BANKING" not in codes and "FINANCIAL INSTITUTIONS/INVESTMENTS/SECURITIES" not in codes:
# 	# 	root.remove(filing)
# 	# 	continue

# set up data that should go in csv
filing_dicts = []
longest_lobbyists = [0, 0]
lobbyists = []
# longest_issues = [0, 0]
# all_issues = []

# from each filing in filtered root, gets data from tree that we want to place in csv
# note how different variables require parsing data tree in different ways
for ind1, filing in enumerate(root.findall("./Filing")):
  d = {}
  d["code"] = "https://lda.senate.gov/api/v1/filings/" + filing.attrib["ID"]
  d["year"] = filing.attrib["Year"]
  d["received"] = filing.attrib["Received"]
  d["type"] = filing.attrib["Type"]
  d["period"] = filing.attrib["Period"]
  d["registrant_name"] = filing.find("Registrant").attrib["RegistrantName"]
  d["registrant_desc"] = filing.find("Registrant").attrib["GeneralDescription"]
  d["client_name"] = filing.find("Client").attrib["ClientName"]
  d["client_desc"] = filing.find("Client").attrib["GeneralDescription"]
  d["client_contact_full_name"] = filing.find("Client").attrib["ContactFullname"]
  # loop through all the associated lobbyists
  for ind2, lobbyist in enumerate(filing.findall("Lobbyists/Lobbyist")):
    # populates list of all issues mentioned
    lobbyist_number = "lobbyist_" + str(ind2)
    if len(lobbyists) < (ind2 + 1):
      lobbyists.append(lobbyist_number)
    if ind2 > longest_lobbyists[0]:
      # if this filing has the most issues, it puts the indicies into longest_issues
      longest_lobbyists = [ind2, ind1]
    d[lobbyist_number] = lobbyist.attrib["LobbyistName"]

  filing_dicts.append(d)

# names csv file to write to
out_file_name = "output.csv"

# writes csv file
with open(out_file_name, "w", newline="\n") as csvfile:
  fieldnames = list(filing_dicts[longest_lobbyists[1]].keys()) + lobbyists
  fieldnames = unique_list(fieldnames)
  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
  writer.writeheader()
  writer.writerows(filing_dicts)
  # for filing in filing_dicts:
  #   writer.writerow(filing)
