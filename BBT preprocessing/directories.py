import os

# contains transcripts fetch from the internet
fetch_directory = "fetched_content"
if not os.path.exists(fetch_directory):
	os.makedirs(fetch_directory)

# contains transcripts with line numbers
parse_directory = "parsed_content"
if not os.path.exists(parse_directory):
	os.makedirs(parse_directory)
