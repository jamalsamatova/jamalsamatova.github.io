import jieba
import jieba.posseg as pseg
txt_file_name = './threekingdoms.txt'
node_file_name = './三国演义-人物节点.csv'
link_file_name = './三国演义-人物连接.csv'

txt_file = open(txt_file_name, 'r', encoding='utf-8')
line_list = txt_file.readlines()
txt_file.close()

jieba.load_userdict('./userdict.txt')

line_name_list = [] 
name_cnt_dict = {}  

ignore_list = ['玄德曰','孔明曰','魏兵','曹兵','文武','伏兵','大将军',
               '诸葛','吴兵','许昌','玄德大','曹军','汝二人','诸侯']

progress = 0  
for line in line_list: 
    word_gen = pseg.cut(line)
    line_name_list.append([])
    
    for one in word_gen:
        word = one.word
        flag = one.flag
        
        if len(word) == 1:  
            continue
        
        if word in ignore_list:  
            continue

        if word == '孔明':
            word = '诸葛亮'
        elif word == '玄德' or word == '刘玄德':
            word = '刘备'
        elif word == '云长' or word == '关公':
            word = '关羽'
        elif word == '后主':
            word = '刘禅'  
            
        if flag == 'nr': 
            line_name_list[-1].append(word)
            if word in name_cnt_dict.keys():
                name_cnt_dict[word] = name_cnt_dict[word] + 1
            else:
                name_cnt_dict[word] = 1


relation_dict = {}

name_cnt_limit = 100  

for line_name in line_name_list:
    for name1 in line_name:
        if name1 in relation_dict.keys():
            pass  
        elif name_cnt_dict[name1] >= name_cnt_limit: 
            relation_dict[name1] = {}  
        else: 
            continue
        
        for name2 in line_name:
            if name2 == name1 or name_cnt_dict[name2] < name_cnt_limit:  

                continue
            
            if name2 in relation_dict[name1].keys():
                relation_dict[name1][name2] = relation_dict[name1][name2] + 1
            else:
                relation_dict[name1][name2] = 1

item_list = list(name_cnt_dict.items())
item_list.sort(key=lambda x:x[1],reverse=True)

node_file = open(node_file_name, 'w', encoding='utf-8') 
node_file.write('Name,Weight\n')
node_cnt = 0  
for name,cnt in item_list: 
    if cnt >= name_cnt_limit:  
        node_file.write(name + ',' + str(cnt) + '\n')
        node_cnt = node_cnt + 1
node_file.close()

link_cnt_limit = 10 

link_file = open(link_file_name, 'w', encoding='utf-8')
link_file.write('Source,Target,Weight\n')
link_cnt = 0  
for name1,link_dict in relation_dict.items():
    for name2,link in link_dict.items():
        if link >= link_cnt_limit:  
            link_file.write(name1 + ',' + name2 + ',' + str(link) + '\n')
            link_cnt = link_cnt + 1
link_file.close()

from pyecharts import options as opts
from pyecharts.charts import Graph

node_file_name = './三国演义-人物节点-分类.csv' 
link_file_name = './三国演义-人物连接.csv'
out_file_name = './threekingdoms_relations.html'

node_file = open(node_file_name, 'r', encoding='utf-8')
node_line_list = node_file.readlines()
node_file.close()
del node_line_list[0]
link_file = open(link_file_name, 'r', encoding='utf-8')
link_line_list = link_file.readlines()
link_file.close()
del link_line_list[0]  
categories=[{}, {'name':'魏'}, {'name':'蜀'},{'name':'吴'},{'name':'群'}]

node_in_graph = []
for one_line in node_line_list:
    one_line = one_line.strip('\n')
    one_line_list = one_line.split(',')
    node_in_graph.append(opts.GraphNode(
            name=one_line_list[0], 
            value=int(one_line_list[1]), 
            symbol_size=int(one_line_list[1])/20,  
            category=int(one_line_list[2])))  
link_in_graph = []
for one_line in link_line_list:
    one_line = one_line.strip('\n')
    one_line_list = one_line.split(',')
    link_in_graph.append(opts.GraphLink(
            source=one_line_list[0], 
            target=one_line_list[1], 
            value=int(one_line_list[2])))

c = Graph()
c.add("", 
      node_in_graph, 
      link_in_graph, 
      edge_length=[10,50], 
      repulsion=5000,
      categories=categories, 
      layout="force",  
      )
c.render(out_file_name)