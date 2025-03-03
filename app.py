from flask import Flask, render_template, request#, jsonify
#from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString=request.form['content'].replace(" ","")
            flipkart_url= "https://www.flipkart.com/search?q=" + searchString
            uclient=uReq(flipkart_url)
            flipkartcode=uclient.read()
            flipkart_html=bs(flipkartcode,"html.parser" )
            flipkart_data=flipkart_html.find_all("div",class_="cPHDOP col-12-12")
            flipkart_product="https://www.flipkart.com" + flipkart_data[2].div.div.div.a['href']
            
            prodres=requests.get(flipkart_product)
            prodres.encoding='utf-8'
            prod_html=bs(prodres.text,"html.parser" )
            allreview= prod_html.find_all("div",class_="col pPAw9M")
            a1=allreview[0].find_all("a")
            
            href_value = a1[-1]['href']
            allcommentpage="https://www.flipkart.com" + href_value
            acp_request=requests.get(allcommentpage)
            acp_request.encoding='utf-8'
            acp_html=bs(acp_request.text,"html.parser" )

            all_page=acp_html.find_all('a', class_="cn++Ap")
            m=all_page[0]
            m=m['href']
            m=m[:-1]
            
            filename= searchString + ".csv"
            fw=open(filename,"w")
            headers="comment \n"
            fw.write(headers)
            reviews=[]
            
            p=request.form['num_pages']
            p=int(p) + 1

            for i in range(1,p):
                u= "https://www.flipkart.com"+m+ str(i)
                comment_request=requests.get(u)
                comment_request.encoding='utf-8'
                comment_html=bs(comment_request.text,"html.parser" )
                comments=comment_html.find_all("div", class_="ZmyHeo")
                for i in comments:
                    try:
                        custComment=i.div.div.text
                        mydict={"comment": custComment}
                        reviews.append(mydict)
                    except Exception as e:
                        logging.info(e)
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html',reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return "something wnt wrong"
    
    else:
        return render_template('index.html')
    
if __name__ == '__main__':
    app.run(debug=True)
    