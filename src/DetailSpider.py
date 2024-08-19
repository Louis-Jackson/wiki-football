import wikipedia
from DBInit import DBInit
from lxml import etree
import requests
from loguru import logger
import json
import re
from urllib.parse import unquote

class DetailSpider:
     def __init__(self) -> None:
          self.db = DBInit(table_name="detail").db
          pass
     
     
     def get_result(self):
          table_list = ["players", "referee", "team", "venue"]
          result = []
          for table in table_list:
               sql = f"SELECT * FROM {table}"
               result_temp = self.db.find(sql, to_json=True)
               for item in result_temp:
                    item["TABLE_NAME"] = table
               result.extend(result_temp)
          return result

     def infobox_get(self, ID, url, table_name):
          
          def get_content(url):
               # 发送HTTP请求获取网页内容
               response = requests.get(url)
               response.raise_for_status()  # 检查请求是否成功
               html_content = response.content  # 获取响应内容
               return html_content

          def parse_html(html_content):
               # 使用lxml解析HTML内容
               parser = etree.HTMLParser()
               content = etree.fromstring(html_content, parser)
               return content

          def unified_string(object):
               # 如果是一个列表，则转换为字符串，如果是字符串则直接返回
               if type(object) == list:
                    return ''.join(object)
               if type(object) == str:
                    return object

          def extract_infobox(content):
               '''
               维基百科页面中的侧边栏中有一些结构化的表，table表的class="infobox"，可以直接取来作为结构化的数据，作为当前实体的结构化信息
               :param infobox:
               :return:
               '''
               infobox = content.xpath(".//table[contains(@class,'infobox')]//tr")
               knowledge = dict()
               header_knowledge = dict()
               for ei, i in enumerate(infobox):
                    th_header = i.xpath(".//th[contains(@class,'infobox-header')]")
                    th_text = i.xpath(".//th//text()")  # 在infobox中，属性都是用粗体表示的，对应于th标签，维基百科比较好处理
                    if len(th_text) == 0:
                         continue

                    th_text = th_text[0]
                    if len(th_header) != 0:
                         th_header = th_header[0]
                         td_header = th_header.xpath(".//text()")[0].strip()
                         knowledge = dict()  # 说明当前行是属性的结束，清空knowledge
                         header_knowledge[td_header] = knowledge
                         
                    td_text = '\t'.join([unified_string(tdi.xpath(".//text()")) for tdi in i.xpath(".//td")])
                    
                    if th_text is not None and th_text != '' and td_text is not None and td_text != '':  # 说明当前行没有属性值，或者不是属性
                         knowledge[th_text] = td_text.replace(' ', '')
                         header_knowledge[td_header] = knowledge
               return header_knowledge
          
          html_content = get_content(url)
          content = parse_html(html_content)
          infobox_data = extract_infobox(content)
          json_infobox_data = json.dumps(infobox_data, ensure_ascii=False)
          json_infobox_data = json_infobox_data.replace(r"\n", "").replace(r"\t", r"    ")
          sql = f"UPDATE {table_name} SET INFOBOX = '{json_infobox_data}' WHERE ID = {ID}"
          logger.info(sql)
          self.db.update(sql)
          
     @staticmethod
     def fuzzy_search(data, key):
          results = []
          for k, v in data.items():
               if key in k:
                    results.append((k,v))
               if isinstance(v, dict):
                    results.extend(DetailSpider.fuzzy_search(v, key))
          return results
     
     @staticmethod
     def get_page(url):
          decoded_url = unquote(url)
          title = decoded_url.split("/")[-1]
          page = wikipedia.page(title)
          return page
     
     def summary_get(self, ID, url, table_name):
          page = self.get_page(url)
          SUMMARY = page.summary.replace("'",r"\'")
          sql = f"UPDATE {table_name} SET SUMMARY = '{SUMMARY}' WHERE ID = {ID}"
          logger.info(sql)
          self.db.update(sql)
          
     def image_get(self, ID, url, table_name):
          page = self.get_page(url)
          IMAGES = json.dumps(page.images, ensure_ascii=False)
          sql = f"UPDATE {table_name} SET IMAGES = '{IMAGES}' WHERE ID = {ID}"
          logger.info(sql)
          self.db.update(sql)
     
     def content_get(self, ID, url, table_name):
          
          def extract_sections(text):
               sections = {}
               current_section = None
               current_subsection = None
               current_subsubsection = None
               
               lines = text.split('\n')
               
               for line in lines:
                    # Ignore empty lines
                    if not line.strip():
                         continue

                    # Match level 2 headers
                    level2_match = re.match(r'^== (.+) ==$', line)
                    if level2_match:
                         current_section = level2_match.group(1).strip()
                         sections[current_section] = {}
                         current_subsection = None
                         current_subsubsection = None
                         continue
                    
                    # Match level 3 headers
                    level3_match = re.match(r'^=== (.+) ===$', line)
                    if level3_match:
                         if current_section:
                              current_subsection = level3_match.group(1).strip()
                              sections[current_section][current_subsection] = {}
                         current_subsection = None
                         continue
                    
                    # Match level 4 headers
                    level4_match = re.match(r'^==== (.+) ====$', line)
                    if level4_match:
                         if current_section and current_subsection:
                              current_subsubsection = level4_match.group(1).strip()
                              sections[current_section][current_subsection][current_subsubsection] = []
                         continue
                    
                    # Add content to the current section/subsection/subsubsection
                    if current_section and current_subsection and current_subsubsection:
                         sections[current_section][current_subsection][current_subsubsection].append(line.strip())
                    elif current_section and current_subsection:
                         sections[current_section][current_subsection].setdefault(None, []).append(line.strip())
                    elif current_section:
                         sections[current_section].setdefault(None, []).append(line.strip())
               
               
               # Convert lists to strings and ensure proper formatting
               for section in sections:
                    for subsection in sections[section]:
                         if isinstance(sections[section][subsection], dict):
                              for subsubsection in sections[section][subsection]:
                                   if sections[section][subsection][subsubsection]:
                                        sections[section][subsection][subsubsection] = ''.join(sections[section][subsection][subsubsection]).strip()
                         elif isinstance(sections[section][subsection], list):
                              sections[section][subsection] = ''.join(sections[section][subsection]).strip()
               
               # Flatten sections with no subsections
               for section in sections:
                    if isinstance(sections[section], dict):
                         if None in sections[section]:
                              sections[section] = sections[section][None]
                         else:
                              sections[section] = sections[section]
                    elif sections[section]:
                         sections[section] = sections[section]
               
               return sections
     
          
          page = self.get_page(url)
          
          self.summary_get(ID, url, table_name)
          
          wiki_content = page.content.replace(page.summary, "")
          sections = extract_sections(wiki_content)
          
          json_sections = json.dumps(sections, ensure_ascii=False)
          CONTENT = json_sections.replace(r"\n", r"\\n").replace(r"\t", r"\\t").replace(r"'",r"\'").replace(r'"',r'\"')
          
          sql = f"UPDATE {table_name} SET CONTENT = '{CONTENT}' WHERE ID = {ID}"
          logger.info(sql)
          
          self.db.update(sql)
               
     def run(self, keyword):
          
          result = self.get_result()
          
          if keyword == "infobox":
               for item in result:
                    try:
                         self.infobox_get(item["ID"], self.fuzzy_search(item, "URL")[0][1], item["TABLE_NAME"])
                    except Exception as e:
                         logger.error(item["ID"])
                         logger.error(e)
          elif keyword == "image":
               for item in result:
                    try:
                         self.image_get(item["ID"], self.fuzzy_search(item, "URL")[0][1], item["TABLE_NAME"])
                    except Exception as e:
                         logger.error(item["ID"])
                         logger.error(e)
          elif keyword == "content":
               for item in result:
                    try:
                         self.content_get(item["ID"], self.fuzzy_search(item, "URL")[0][1], item["TABLE_NAME"])
                    except Exception as e:
                         logger.error(item["ID"])
                         logger.error(e)
          pass