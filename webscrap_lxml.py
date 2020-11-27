#Script para extrair dados de um site com dados reais de jogos de futebol (cornerprobet)
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from lxml import etree
from datetime import date
import cx_Oracle


#Setup da Base Dados Oracle
dsn_tns = cx_Oracle.makedsn('192.168.56.107', '1521', 'orafut')
conn = cx_Oracle.connect(user=r'orafut', password='orafut', dsn=dsn_tns, encoding="UTF-8", nencoding="UTF-8")

#Abrindo a Sessão no Oracle
c = conn.cursor()

#Definindo o Driver que é o Edge
DRIVER_PATH = 'd:\chromedriver\msedgedriver.exe'
driver = webdriver.Edge(executable_path=DRIVER_PATH)

#pagina de login
url='https://cornerprobet.com/login.php'
driver.get(url)

#Buscar os elementos Usuario e Password
username = driver.find_element_by_id("username")
password = driver.find_element_by_id("password")

 
#Envio do usuario e password para o Site
username.send_keys("11111111")
password.send_keys("11111111")


#Buscar o botão Submit com o Xpath e simular o Click
xpath = '//*[@id="app"]/div[2]/section/div[2]/div/button'
button = driver.find_element_by_xpath(xpath);
button.click();

#Um Segundo de Espera para o carregamento da pagina
time.sleep(1)
page = driver.page_source


#Como os dados estão sempre a serem atualizados criei um loop infinito
i=1
while i!=0: #infinity loop
    
     #Registro no inicio do processo para futuro calculo de espera
     start = time.time() 
     
     #busca a pagina com os dados a serem extraidos
     driver.get('https://cornerprobet.com/live.php')
     
     #Loop para esperar que pagina carregue.. ( NOta: a pagina tem uma script que faz refresh de 10 em 10 segundos.)
     while driver.find_elements_by_css_selector('div.games_list_item') == []:
         time.sleep(0.5)
         
     #Comando para ir para o final da pagina para que todos os dados seja capturados
     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
     page = driver.page_source
     
     #Usando o BeautifulSoup e lxml para processamento. O uso do LXML é porque o BeautifulSoup não permite procura por Xpath
     soup = BeautifulSoup(page, 'html.parser')
     dom = etree.HTML(str(soup))
     
     #Inicialização da Lista de todos os Jogos
     matches=[]
     
     #Inicialização do ID do jogos a serem processados 
     game_num=1
     # Como não se sabe o numero de Jogos a serem processados, definição de um numero alto de jogos para serem processados
     while game_num < 10000000:
        #Inicialização da Lista de um Jogo
        match=[]
        
        # No caso de nao haver mais jogos a serem processado o valor do elemento  é nulo e sai do loop de 10000000 Jogos
        if  dom.xpath('/html/body/div[2]/section[2]/div[2]/div[2]/div['+str(game_num)+']') ==[]:
            break
      
        #PEga o valor do id do Jogo a ser processado. 
        id_txt= dom.xpath('/html/body/div[2]/section[2]/div[2]/div[2]/div['+str(game_num)+']')[0].get('id')  
        
        #Extracao dos dados usando o xpath
        match.append(dom.xpath('/html/body/div[2]/section[2]/div[2]/div[2]/div['+str(game_num)+']')[0].get('data-pressure-index'))
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[1]/span[1]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[1]/div[1]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[8]/div/div[1]/span')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[16]/div/div[1]/span')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[8]/div/div[2]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[16]/div/div[2]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[9]/div[1]/div[1]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[10]/div[1]/div[1]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[11]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[12]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[13]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[14]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[15]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[17]/div[1]/div[1]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[18]/div[1]/div[1]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[19]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[20]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[21]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[22]')[0].text)
        match.append(dom.xpath('//*[@id="'+id_txt+'"]/div[3]/div[23]')[0].text)
        match.append(date.today().strftime("%d/%m/%Y") + " - "+time.strftime("%H:%M:%S", time.localtime()))
      
        #Acrescenta o jogo na lista de jogos
        matches.append(match)
        game_num=game_num+1
     
     #PAra cada Jogo processado, sera guardado numa tabela na base de dados ORacle atraves da chamada de um função ORacle.
     for match_ins  in  matches:
         proc_ind = c.callfunc('INS_CORNERPRO_TMP',float,[match_ins[0],match_ins[1],match_ins[2],match_ins[3],match_ins[4],match_ins[5],match_ins[6],match_ins[7],match_ins[8],match_ins[9],match_ins[10],match_ins[11],match_ins[12],match_ins[13],match_ins[14],match_ins[15],match_ins[16],match_ins[17],match_ins[18],match_ins[19],match_ins[20],match_ins[21],match_ins[22]])
         if proc_ind !=0:
              print ('----ERROR---'+str(proc_ind)+'-------'+id_txt)     
           
     #Como a extracao é feita por minuto, calculo  do tempo de espera para o proximo processamento.
     wait_sec=60-round(time.time()-start, 2)
     print("waiting time->"+str(wait_sec))
     if wait_sec >0 :
        time.sleep(wait_sec)
