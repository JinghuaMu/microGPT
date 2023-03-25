# %% [markdown]
# # Settings (empty)

# %%
# import configparser
# try:
#    config = open("config.ini")
# except FileNotFoundError:
#    API = input("Please Enter Open AI API:")
# else: 
#    pass

# %% [markdown]
# # API test

# %%
import openai
import re
openai.api_key = ""

# %%


# %%
def ask_abs(text,Require="",question="",usage=False):
   default_require = "Please answer my following questions in the most concise and precise manner possible, without answering complete sentences:"
   default_Qabs = '''
         1. How many new strains have been discovered? Just return the number.\n
         2. What's the name of those new strains? Just return the names.\n
         3. What lineage does this species belong to? Use '-' to link different levels\n
         4. Where dose this strain come from? Just return the place.\n 
         5. What the characteristics of these strains?\n
         6. What its best optimal growth environment?\n
         7. What is the metabolic profile of the strain?\n"
   '''
   if not question:
      question = default_Qabs
   if not Require:
      Require = default_require
   Prompt = "{Require}:\n{Abstract}\nQuestions:\n{Question}".format(Require = Require, Abstract = text, Question = question)
   response = openai.Completion.create(
     model="text-davinci-003",
     prompt=Prompt,
     temperature=0,
     max_tokens=200,
     top_p=1,
     frequency_penalty=0,
     presence_penalty=0
   )
   Answer = response['choices'][0]['text']
   pattern = r"\d+\.\s+(.*)"
   Answer_list = re.findall(pattern,Answer)
   Answer_list = [i.encode("utf8") for i in Answer_list]
   if usage:
      print(f'{response["usage"]["prompt_tokens"]} prompt tokens used.')
   return Answer_list


# %%


# %% [markdown]
# # Parse article

# %%
import requests
from bs4 import BeautifulSoup

def get_meta_info(url,warning = False):
   #Send HTTP request
   headers = {
       'User-Agent':
       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
   }
   try:
      response = requests.get(url,headers,timeout=10)
      if '404' in response.url:
           raise Exception('No data found for this link: '+source_url)
      Nopage = re.compile(r'Page Not Found')
      if Nopage.search(response.text):
         if warning:
            raise Exception("Page Not Found")

      #Redirect the page
      url_head = "https://www.microbiologyresearch.org/"
      match_url = re.search(r'data-fullTexturl="(.*?)"',response.text)
      if match_url:
         url_adhere = match_url.group(1)
         redirect = url_head + url_adhere
         full_text_url = requests.get(redirect,headers,timeout=10).text
         full_text = requests.get(full_text_url,headers,timeout=10)
      elif warning:
         raise Exception("Can't Redirect")
   except:
      raise

   # Using latin encodeing and drop menu elements
   soup = BeautifulSoup(full_text.text.encode('latin1').decode('utf-8').replace('\u200a','').replace('\u2006','').replace('\u2009',''),features= 'html.parser')
   elements_to_remove = soup.find_all('div', {'class': 'dropDownMenu'})
   for element in elements_to_remove:
       element.decompose()
   elements_to_remove = soup.find_all('div', {'class': 'menuButton'})
   for element in elements_to_remove:
       element.decompose()

   # get meta data
   title = soup.find('h1').text.strip()
   abstract = soup.find('div', {'class': 'articleSection article-abstract'}).text
   abstract = re.sub(r'\\u[0-9a-fA-F]{4}', '',abstract)
   article = soup.find_all('div', {'class': 'articleSection'})
   return {"title":title,"abstract":abstract,"article":article}

# Parsing full-text content
def get_text(article):   
   article_sorted ={"Head":""}
   regex_main = r'<a id=".*?" name=".*?">(.*?)</a><\/div>'
   delim_tag = r'<.*?>'
   current_part = "Head"
   for text in article:
      main_match = re.search(regex_main, str(text))
      if main_match:
         sub_title = re.sub(delim_tag, '', main_match.group(1))
         if sub_title != current_part:
            article_sorted[sub_title]=""
            current_part = sub_title
            for p in text.find_all('p'):
                article_sorted[sub_title] += p.text
      else: 
         for p in text.find_all('p'):
                article_sorted[current_part] += p.text

   for part in article_sorted:
      article_sorted[part] = re.sub(r'\[.*?\]', '',article_sorted[part])
      article_sorted[part] = re.sub(r'\((http\S+)\)', '',article_sorted[part])
      article_sorted[part] = re.sub(r'\(([^)]*http[^)]*)\)', '',article_sorted[part])
      article_sorted[part] = re.sub(r'\\u[0-9a-fA-F]{4}', '',article_sorted[part])
      
   return article_sorted

# %%
# url = 'https://doi.org/10.1099/ijsem.0.004430'
# get_text(get_meta_info(url)["article"])


# %% [markdown]
# # Parse volume

# %%


# %%
# The function return the newest catalog of IJSEM's volume, which is a list of url
def get_volume_list():   
   url_head = "https://www.microbiologyresearch.org"
   all_volume = "https://www.microbiologyresearch.org/content/journal/ijsem/issueslist"
   headers = {
          'User-Agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
      }
   soup = BeautifulSoup(requests.get(all_volume,headers,timeout=10).text,'html.parser')
   volume_list = []
   grab_list = soup.find_all('a')
   pattern = r'"([^"]*)"'
   for a in grab_list:
      volume_list.append(url_head + re.search(pattern, str(a)).group(1))
   return volume_list

# The function return the soup of a volume page which will be used to get the volume info and article list
def parse_volume(url):
   headers = {
          'User-Agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
      }
   url = url + "?pageSize=100&page=1"
   volume_page = requests.get(url,headers,timeout=10)
   soup = BeautifulSoup(volume_page.text)
   return soup

# The function return the volume info, which is a dictionary of title, date and year
def get_volume_info(soup):
   title = soup.find("meta",  attrs={"name": "citation_title"})["content"]
   date = soup.find("meta",  attrs={"name": "citation_date"})["content"]
   year = soup.find("meta",  attrs={"name": "citation_year"})["content"]
   info = {"title":title,"date":date,"year":year}
   return info

# The function return the article list, which is a list of url
def get_article_list(soup):
   article_block = soup.find('div', {'class': 'issueTocContents table-wrapper'})
   article_block = article_block.find_all('ul', {'class': 'list-unstyled'})
   # Find the block of New Taxa
   taxa_block_pos = -1
   pattern = r'<span class="heading1">\nNew [Tt]axa\n</span>'
   for i in range(len(article_block)):
      match = re.search(pattern,str(article_block[i]))
      if match: taxa_block_pos = i
   if taxa_block_pos == -1: return []
   else:
      taxa_block = str(article_block[taxa_block_pos])
      
   # Find the block of New Species in each region
   pattern_field = r'(?<=<span class="tocheading2">\n)\w+(?=\n<\/span>)'
   taxa_list = [*re.finditer(pattern_field,taxa_block)]
   pos = [i.start() for i in taxa_list]+[len(taxa_block)]
   taxa = [i.group() for i in taxa_list]
   article_list = {}
   for i in range(len(taxa)):
      sub_block = taxa_block[pos[i]:pos[i+1]]
      pattern_doi = r'(?<=href=")https://doi.org/10.1099/ijsem.0.\d+'
      article_list[taxa[i]] = re.findall(pattern_doi,sub_block)
   return article_list

# %% [markdown]
# # Running test

# %%
# Little test

# A = []
# for i in get_article_list(parse_volume(get_volume_list()[1])).values():
#    A = A+i

# get_text(get_meta_info(A[3])["article"])["Description of Muricauda spongiicola sp. nov."]
# URL = "https://doi.org/10.1099/ijsem.0.005691"
# a = get_meta_info(URL)["article"]

# text = ' <div class="articleSection"><div class="sectionDivider"><div class="tl-main-part title"><a id="s9" name="s9">Description of <span class="jp-italic">Acetomicrobiaceae</span> fam. nov.</a></div><div class="clearer"> </div></div></div>'
# regex_main = r'<a id=".*?" name=".*?">(.*?)</a><\/div>'
# main_match = re.search(regex_main, text)
# print(main_match.group(1))



# %%
# The function return the meta info of each article and the specific answer of givin question
# And save the data form one issue into a csv file
# Description of parameters:
# volume_range: an array of volume number that will be used to make the dataset
# year_limit: the year limit of the dataset, 0 means no limit
# require: the promote to chatGPT that will be used to make the dataset, blank means default
# question: the question to chatGPT that will be used to make the dataset, blank means default
# mode: the mode of the dataset, "strain" means each strain will be a sample, 
# "article" means each article will be a sample
def establish_dataset(volume_range = [],year_limit=0,require="",question="",mode = "strain"):
   import csv
   import os 
   # get the list of volume
   volume_list = get_volume_list()
   # filter the volume list
   if volume_range:
      volume_list_neo = []
      for i in volume_list:
         if int(i.split('/')[-2]) in volume_range:
            volume_list_neo.append(i)
      volume_list = volume_list_neo
   # get the info of each volume
   for vol_url in volume_list:
      try:
         cur_vol = parse_volume(vol_url)
         cur_vol_info = get_volume_info(cur_vol)
         print("Current Volume: ",cur_vol_info["title"])
      except:
         print("Read volume failed!")
         continue
      # filter the volume by year and get the article list from each volume
      if (int(cur_vol_info["year"]) > year_limit):
         cur_vol_article_list = get_article_list(cur_vol)
         if not cur_vol_article_list:
            print("No article found!")
            continue
         # main loop of asking question to chatGPT
         num_info = [print(i,":",len(j)) for i,j in cur_vol_article_list.items()]
         span = sum([len(j) for j in cur_vol_article_list.values()])
         cur_num = 0
         # check if the file already exists
         if not os.path.exists(cur_vol_info["title"]+".csv"):
            with open(cur_vol_info["title"]+".csv", 'w', newline='', encoding = "utf-8") as csvfile:
               writer = csv.writer(csvfile, delimiter='\t')
               for region, url_list in cur_vol_article_list.items():
                  for article_url in url_list:
                     cur_num += 1
                     # get the meta info and text of each article
                     try:
                        if mode == "strain":
                           meta_info = get_meta_info(article_url)
                           text = get_text(meta_info["article"])
                        if mode == "article":
                           meta_info = get_meta_info(article_url)
                     except:
                        print("Read failed!")
                        continue
                     progess = "({}/{})".format(cur_num,span)
                     print(progess+"Currently parsing article:  ",meta_info["title"])

                     if mode == "strain":
                        # get the strain info
                        # the metainfos are: article_url, title, region, strain, answer
                        count = 0
                        for section, section_text in text.items():
                           if re.search("[Dd]escription",section):
                              count += 1
                              strain = section.split("of")[-1].strip(" ")
                              answer = ask_abs(section_text,require,question)
                              newline = [article_url.encode("utf8")] + [meta_info["title"].encode("utf8")] + [region.encode("utf8")] + [strain.encode("utf8")] + answer
                              writer.writerow(newline)
                              csvfile.flush()
                        if count == 0:
                           print("No description found!")
                        else:
                           print("Successfully written {} strains to the file!".format(count))
               
                     if (mode == "article") or (mode == "strain" and count == 0):
                        # get the abstract info 
                        # the metainfos are: article_url, title, region, strain, answer
                        answer = ask_abs(meta_info["abstract"],require,question)
                        newline = [article_url.encode("utf8")] + [meta_info["title"].encode("utf8")] + [region.encode("utf8")] + ["None"] + answer
                        writer.writerow(newline)
                        csvfile.flush()
                        if not mode == "strain":
                           print("Successfully written to the file!")
                        else:
                           print("Written info from the abstract")
         else:
            print("File already exist!")
      else:
         print("Volume reach the year limit!")
         break


# %%
r1 = "Please complete the setences by filling the blank in brackets:"
q1 = '''
         1. There are () number of new strains was found.\n
         2. The name of those strains are ().\n
         3. The full lineage of the strain is ().\n
         4. The strain was extracted from ().\n 
         5. The characteristic of the strain is ().\n
         6. The best optimal growth environment is ().\n
         7. The metabolic profile of the strain is ().\n"
   '''

establish_dataset([73],require=r1,question=q1)

# %%



