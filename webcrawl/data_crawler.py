from bs4 import BeautifulSoup as bs
import urllib2
import Queue
import sqlite3

class Question:
    def __init__(self, question, ref, num, parts):
        self.question = question
        self.ref = ref
        self.num = num
        self.parts = parts
        self.ans = 'None'
        
    def add_ans(self, ans):
        self.ans = ans
        
    def __str__(self):
        q = ""
        q += "question: " + self.question +"\n"
        q += "ref: "+self.ref + "\n"
        q += "parts: "+ str(self.parts)+"\n"
        q += "ans: " + str(self.ans) + "\n"
        return q

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None

def create_rec(conn, q):
    sql = ''' INSERT INTO questions(q_text, ref, num, ops, ans) VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    question_data = (q.question, q.ref, str(q.num), str(q.parts), q.ans)
    cur.execute(sql, question_data)
    return cur.lastrowid

doc_name = 'sites.html'
db_file = '../trivia.db'

with open(doc_name) as fp:
    soup = bs(fp, 'html.parser')

valid_links = [link.get('href') for link in soup.find_all('a') if not 'bible-quiz-index' in str(link)]

conn = create_connection(db_file)

queue = Queue.Queue()
for i in range(0, len(valid_links), 2):
    question_link = urllib2.urlopen(valid_links[i]).read()
    question_html = bs(question_link, 'html.parser')
    answer_link = urllib2.urlopen(valid_links[i+1]).read()
    answer_html = bs(answer_link, 'html.parser')
    
    for li in question_html.find_all('li', 'question'):
        for ul in li.find_all('ul', 'question-text'):
            parts = [text.encode('ascii', 'ignore') for text in ul.stripped_strings]
            ques = parts.pop(0)
            ref = 'None'
            if ul.find_all('span') != []:
                ref = parts.pop(0)
            queue.put(Question(ques, ref, len(parts), parts))
    
    answer_parts = []
    for li in answer_html.find_all('li', 'question'):
        for ul in li.find_all('ul', 'question-text'):
            answer_parts.append([text.encode('ascii', 'ignore') for text in ul.stripped_strings])

    
    for j in range(len(answer_parts)):
        q = queue.get()
        if q.ref == 'None':
            q.add_ans(answer_parts[j][1])
        else:
            q.add_ans(answer_parts[j][2])
        create_rec(conn, q)
    conn.commit()
conn.close()