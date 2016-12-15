import json

def is_ascii(s):
    return all(ord(c) < 128 for c in s)


"""
Function to get Reddit data from corpus
"""
def getFileData(file, N, data):
    with open(file) as myfile:
        json_block = []
        i = 0
        for line in myfile:
            j_content = json.loads(line)
            # print j_content
            json_block.append(j_content)
            i = i + 1

            if (i > N):
                break
    return json_block

"""
Function to parse JSON data from corpus and create HTML links to data
"""
def createHTMLLinks(json_block):

    links_parent = open("links_parent.txt", "w")
    links_post = open("links_post_id.txt", "w")
    for j in json_block:
        if is_ascii(s=j["body"]):
            if ' /s ' in j["body"]:
                if is_ascii(s=j["body"]):

                        # print j["body"]

                    link = "https://www.reddit.com/r/"
                    link_id = str(j["link_id"]).split("_")[1]
                    parent_id = str(j["parent_id"]).split("_")[1]
                    link_parent = link + str(j["subreddit"]) + "/comments/" + str(link_id) + "//" + str(parent_id)
                    link_post = link + str(j["subreddit"]) + "/comments/" + str(link_id) + "//" + str(j["id"])
                    # links.append(link)
                    links_parent.write(link_parent)
                    links_parent.write("\n")
                    links_post.write(link_post)
                    links_post.write("\n")





if __name__ == "__main__":

    #uses Reddit corpus
    json_blocks = getFileData(file="RC_2016-10", N=500, data='test')

    #createHTMLLinks
    createHTMLLinks(json_blocks)
