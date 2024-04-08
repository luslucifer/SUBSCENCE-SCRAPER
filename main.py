from bs4 import BeautifulSoup
from lxml import html 
import requests
import io 
import zipfile
import re 
from thefuzz import fuzz
from flask import Flask,request,jsonify
from urllib.parse import quote,unquote
import os
import inflect 
root = "https://subscene.com"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
}

headersid = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNmYyYTllOWIwZjVlZWQ4MWI0Y2FiZTM1ZDVhOWMxYiIsInN1YiI6IjY0ZmViZGFhZGI0ZWQ2MTAzODU1MjkyMiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.3tF5McjnvghWciYB--s1b7Aj4hQW4SCRpIkaXn8Feig"
}
link = 'https://subscene.com/subtitles/arabic-text/P8CLcuLwyZUfcUIfBmr-6QG0VAfMjtQXUo5jS-PzQabWciqzcx97X-BF2OszgXAtnZr_QRe5ZR3-E45JcXW9y3PTIskBNjuqEVuyB8r4ne3yiHTeN2cElYqAVe7ECA510'

# host = request.host

inflict1 = inflect.engine()
class DwnloadLink:
    def search_subtitles(self,q: str):
        r = requests.post(f"{root}/subtitles/searchbytitle", headers=headers, params={"query": q})
        
        soup = BeautifulSoup(r.content, "html.parser")

        subtitle_links = []
        for a in soup.find_all("a"):
            if a.get("href").startswith("/subtitles/"):
                subtitle_links.append({
                    "title": a.text,
                    "url": f"{root}{a.get('href')}"
                })

        return subtitle_links
    def getDownLink(self,url:str):
        r = requests.get(url,headers=headers).text
        soup = BeautifulSoup(r,'html.parser')
        f = soup.find('a',class_='button positive')
        dwn_url = root+f['href']
        return dwn_url
    
    def extractor(self,dwn_link:str) :
        link = self.getDownLink(dwn_link)  
        res = requests.get(link,headers=headers)
        # obj = {}
        # start_time = time.time()
        if res.status_code ==200 :
            with zipfile.ZipFile(io.BytesIO(res.content),'r') as zip_ref : 
                for filename in zip_ref.namelist():
                    try :
                        print(filename)
                        file_content = zip_ref.read(filename)
                        # obj[filename] = file_content
                        return file_content
                    except Exception as err : 
                        print (f' err in extractor : {err}')
        # print(time.time()-start_time)
        # return obj 
    
    def get_page_urls(self,url:str,ss:str|None = None, ep:str|None =None): #https://subscene.com/subtitles/titanic
        res = requests.get(url,headers=headers)
        arr = []
        # print(res.content)
        if res.status_code == 200: 
            soup = BeautifulSoup(res.content , 'html.parser') 
            a_elements= soup.find_all('a')
            for a in a_elements : 
                obj = {}
                x = a.find('span',class_='l r positive-icon')
                spans = a.find_all('span')
                if x!= None and len(spans) ==2 and ss==None: 
                    print(ss)
                    text = x.text 
                    cleaned_string = re.sub(r"[\t\r\n]","",text)
                    obj['lang'] = cleaned_string
                    obj['url'] = root+a['href']
                    obj['text'] =  re.sub(r"[\t\r\n]","",spans[1].text)
                    arr.append(obj)
                elif x!= None and len(spans) ==2 and ss!=None:
                    try :
                        ss=self.numeric_converter_01(ss)
                        ep = self.numeric_converter_01(ep)
                        text = x.text 
                        cleaned_string = re.sub(r"[\t\r\n]","",text)
                        cleaned_t = re.sub(r"[\t\r\n]","",spans[1].text)
                        obj['lang'] = cleaned_string
                        obj['url'] = root+a['href']
                        obj['text'] =  cleaned_t
                        if f'S{ss}E{ep}' in cleaned_t:
                            print('appended ')
                            arr.append(obj)
                    except Exception as err : 
                        print(err)
        return arr
        #print(x.text)
    def numeric_converter_01(self,no:str):
        if len(no) == 1 :
            return '0'+no
        else :
            return no


    def search_result_filtered (self,id:str,ss:str=None):
            if ss!=None:
                url = f"https://api.themoviedb.org/3/tv/{id}?language=en-US"
                res = requests.get(url,headers=headersid).json()
                year = res['first_air_date'][:4]
                title = res['name']
            else :
                url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"
                res = requests.get(url,headers=headersid).json()
                year = res['release_date'][:4]
                title = res['title']



            if ss!= None : 
                word_number = inflict1.number_to_words(int(ss))
                ordial:str = inflict1.ordinal(word_number)
                capi_ordial = ordial.capitalize()

                title = f'{title} - {capi_ordial} Season'
                print(title)
            matchQ = f'{title} ({year})'
            searched_arr = self.search_subtitles(title)
            ratio = 0
            stored_obj = {}
            for  obj in searched_arr: 
                stored_obj = obj
                t = obj['title']
                similarity_ratio = fuzz.ratio(t, matchQ)
                # Using fuzz.partial_ratio
                partial_ratio = fuzz.partial_ratio(t, matchQ)
                # Using fuzz.token_sort_ratio
                token_sort_ratio = fuzz.token_sort_ratio(t, matchQ)
                # Using fuzz.token_set_ratio
                token_set_ratio = fuzz.token_set_ratio(t, matchQ)
                total_ratio = similarity_ratio +partial_ratio+token_sort_ratio+token_set_ratio
                if ratio < total_ratio :
                    ratio = total_ratio

                if ratio ==400 :
                    print('for loop breaked!!!!!!!!!!!!!')
                    return obj 
            return stored_obj



    def main(self,id,ss:str=None,ep:str = None): 
        searched_obj= self.search_result_filtered(id,ss)
        sub_url = searched_obj['url']
        available_subs_arr = self.get_page_urls(sub_url,ss,ep)
        return available_subs_arr
        # print(e)

app = Flask(__name__)

@app.route('/')
def main():
    # host = request.
    with open('index.html','r') as file : 
        htmlx = file.read()
    return htmlx

@app.route('/sub/<id>')
def movie_subs_list(id): 
    host = request.host
    ss = request.args.get("ss",None)
    ep = request.args.get("ep",None)
    dwn = DwnloadLink()
    arr = dwn.main(id,ss,ep)
    for obj in arr:
        encoded_url = quote(obj['url'], safe='~()*!\'')
        obj['url'] = f'https://{host}/x/{encoded_url}.srt'

    return jsonify(arr)  # Return JSON response
    

@app.route('/x/<path:url>')
def dwn_srt(url):
    decoded_url = unquote(url)
    decoded_url = decoded_url.replace('.srt','')
    dwn = DwnloadLink()
    return  dwn.extractor(decoded_url)
        

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', True)
    app.run(host=host, port=port, debug=debug)
    
