import io, os, re, requests, shutil, time

from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

PSA = None
marque = ""
##debug = 0
Downloader = None
pathMain = ""
pathDocs = ""
pathDocsFiles = ""
##proxy = "socks5://127.0.0.1:9150"
##login = "AN12345678"
##passw = "password"

def main():
  debugprint("\n" * 40)
  debugprint("Start")

  window = Tk()
  window.configure(background='pink')
  window.title("Free Servicebox")
  window.geometry('600x400')
  window.resizable(0, 0)
  window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoP.png'))
  window.call('wm', 'attributes', '.', '-topmost', True)

  dummyNW = Label().grid(column = 0, row = 0)
  dummySE = Label().grid(column = 5, row = 6)
  logoP = ImageTk.PhotoImage(file = "logoP.png")
  logoC = ImageTk.PhotoImage(file = "logoC.png")
  logoO = ImageTk.PhotoImage(file = "logoO.png")
  logoD = ImageTk.PhotoImage(file = "logoD.png")

  bP = Button(window, image = logoP, command=lambda: window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoP.png'))).grid(column = 1, row = 1)
  bC = Button(window, image = logoC, command=lambda: window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoC.png'))).grid(column = 2, row = 1)
  bO = Button(window, image = logoO, command=lambda: window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoO.png'))).grid(column = 3, row = 1)
  bD = Button(window, image = logoD, command=lambda: window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoD.png'))).grid(column = 4, row = 1)

  go1 = Button(window, text = "Начинаем", command = psa1paid).grid(column = 1, row = 2)
  tt1 = Label(text = "В открывшемся окне браузера нужно:" + "\n" + \
              "1. авторизоваться и пройти капчу, если она появится;" + "\n" + \
              "2. ввести VIN или выбрать автомобиль и перейти\n     в раздел \"Каталог запасных частей\".").grid(sticky = "W", column = 2, row = 3, columnspan = 4)
  go2 = Button(window, text = "Продолжаем", command = psa2paid).grid(column = 1, row = 4)

  Grid.columnconfigure(window, 0, weight=1)
  Grid.columnconfigure(window, 5, weight=1)
  Grid.rowconfigure(window, 0, weight=1)
  Grid.rowconfigure(window, 2, weight=1)
  Grid.rowconfigure(window, 5, weight=1)
  Grid.rowconfigure(window, 6, weight=1)

  window.mainloop()
  

def debugprint(s):
  if debug == 1:
    print(s)

#-------------------------------------------------
def DownloadInit(dirname):
  global PSA
  global Downloader
  global pathMain
  global pathDocs
  global pathDocsFiles
  
  pathMain = "SB\\" + dirname
  pathDocs = pathMain + "docs\\"
  pathDocsFiles = pathDocs + "files\\"
  
  os.makedirs(pathDocs, exist_ok=True)
  os.makedirs(pathDocsFiles, exist_ok=True)
  
  cookies = PSA.get_cookies()
  Downloader = requests.Session()
  for cookie in cookies:
    Downloader.cookies.set(cookie['name'], cookie['value'])
#=================================================

#-------------------------------------------------
def DownloadFile(url, filename = "", overwrite = True):
  if "//" in url:
    return
  global Downloader
  url = url.strip("\n")
  if os.path.splitext(url)[1] in (".js", ".css", ".gif", ".jpg"):
    dirname = pathDocsFiles
    DoNotCheckContent = True
  else:
    dirname = pathDocs
    DoNotCheckContent = False
  fn = dirname + (filename if filename != "" else os.path.basename(url))
  if os.path.isfile(fn) and not overwrite and not os.stat(fn).st_size == 0:
    print(".....file " + fn + " exists")
    return
  else:
    print(".....download " + url)
    pass
  DownloadRetriesZeroSize = 3
  DownloadRetriesCheckContent = 5
  DownloadFail = False
  DownloadOK = False
  while (not DownloadOK ) and (not DownloadFail):
    if DownloadRetriesZeroSize > 0:
      stream = Downloader.get(url, stream = True, proxies = dict(http = proxy, https = proxy))
      file = open(fn, "wb")
      stream.raw.decode_content = True
      shutil.copyfileobj(stream.raw, file)
      file.close()
    if os.stat(fn).st_size == 0:
      DownloadRetriesZeroSize = DownloadRetriesZeroSize - 1
      DownloadFail = DownloadRetriesZeroSize == 0
      print(f"..........Retry N{4 - DownloadRetriesZeroSize} (zero size) to download {url}")
    else:
      if CheckContentOf(fn) or DoNotCheckContent:
        DownloadOK = True
      else:
        DownloadRetriesZeroSize = 3
        DownloadRetriesCheckContent = DownloadRetriesCheckContent - 1
        DownloadFail = DownloadRetriesZeroSize == 0
        print(f"..........Retry N{4 - DownloadRetriesCheckContent} (incomplete content) to download {url}")
    if DownloadFail:
      print(f".....Fail to download {url}")
  
#=================================================
  
#-------------------------------------------------
##callAction('T73R001A50A','T73R 0 01A50A','AP','1','FCT0512',false);
##http://public.servicebox.peugeot.com/docprAP/affiche.do?ref=T73R001A03A&refaff=T73R%200%2001A03A&idFct=FCT0512
##http://public.servicebox.peugeot.com/docprAC/affiche.do?ref=053801002016A&refaff=0538%2001%20002016A&idFct=FCT0512
##http://public.servicebox.peugeot.com/docprDS/affiche.do?ref=X74E01002060A&refaff=X74E%2001%20002060A&idFct=FCT0512
##http://public.servicebox.peugeot.com/partsOV/affiche.do?ref=K0OP001A71B&refaff=K0OP%200%2001A71B&idFct=FCT0512  
def callAction(url):
  global marque
  u = url.split(",")
  if (u[3] == "1"): #typeDoc == TYPE_PR
    return ("http://public.servicebox.peugeot.com/" + marque + "/affiche.do?" + \
            "ref=" + u[0] + "&refaff=" + u[1] + "&idFct=" + u[4])
#=================================================

#-------------------------------------------------
def cutScriptTag(instr, jsname):
  matches = re.finditer("<script.*?><\/script>", instr)
  s = ""
  for matchNum, match in enumerate(matches, start=1):
    if re.search(jsname, match.group()) == None:
      s = s + match.group()
  return(s if len(s) > 0 else instr)
#=================================================

#-------------------------------------------------
def DocParseAndTransform(filename):
  global pathDocs
  tmpfile = io.open(pathDocs + filename, mode="r", encoding="utf-8")
  docfile = io.open(pathDocs + filename.replace(".txt", ".html"), mode="w", encoding="utf-8")
  urlfile = open(pathDocs + "DocsResourcesUrlList.txt", "a")
  for line in tmpfile:
    t = line.strip("\n")
    if len(t) > 0:
      tresrc = re.search(r"\b(src|href|imgPath|img_details)\b=.??\"([^\"]*)\/(.*?)\\*?\"", t)
      if tresrc:
        str = "http://public.servicebox.peugeot.com/" + marque + "/" + tresrc.group(2) + "/" + tresrc.group(3)
        urlfile.write(str + "\n")
        t = t.replace(tresrc.group(2), "files")
      tredel = re.search(r"( *onDblClick=\"PRDblClick\('.*?'\)\")", t)
      if tredel:
        t = t.replace(tredel.group(1) , "")
      docfile.write(t + "\n")
  docfile.close()
  tmpfile.close()
  urlfile.close()
#=================================================

#-------------------------------------------------
def getCarInfo():
  global PSA
  global marque
  global pathDocs
  infosVehicule = PSA.find_element_by_id("infosVehicule").get_attribute("innerText")
  VIN = PSA.find_element_by_id("short-vin").get_attribute("value")
  if VIN == "VIN/VIS":
    return()
  PSA.get("http://public.servicebox.peugeot.com/docapvAP/caracteristique.do")
  InfoZone = PSA.find_element_by_id("InfoZone")
  ifile = open(pathMain + VIN + ".html", "w")
  ifile.write("<html>" + "\n")
  ifile.write("<head>" + "\n")
  ifile.write("<link href=\"files/main.css\" rel=\"stylesheet\" type=\"text/css\" media=\"all\">" + "\n")
  ifile.write("<script src=\"files/script.js\"></script>" + "\n")
  ifile.write("<title>Service Box</title>" + "\n")
  ifile.write("</head>" + "\n")
  ifile.write("<body>" + "\n")
  ifile.write("<h1>" + infosVehicule + " " + VIN + "</h1>" + "\n")
  for t1 in InfoZone.find_elements_by_xpath("./table"):
    if t1.get_attribute("class") == "table_lst_doc":
      ifile.write("<table class='carinfo'><thead><th align=\"left\">Характеристики автомобиля</th><th>&nbsp;</th></thead>\n<tbody>\n")
      for t2 in t1.find_elements_by_xpath("./tbody/tr"):
        td1 = t2.find_element_by_xpath("./td[@class='infoGenCar']").get_attribute("innerText")
        td2 = t2.find_element_by_xpath("./td[@class='infoCarText']").get_attribute("innerText")
        ifile.write("<tr><td>" + td1 + "</td><td>" + td2 + "</td></tr>\n")
      ifile.write("</tbody></table>\n")
    else:
      infoCarTitreSoulignement = t1.find_element_by_xpath("./tbody/tr[1]/td[1]").get_attribute("innerText") 
      ifile.write("<table class='carinfo'><thead><th colspan=2 align=\"left\">" + infoCarTitreSoulignement + "</th></thead>\n<tbody>")
      tableInfoVeh = t1.find_elements_by_xpath("./tbody/tr[2]/td/table[@class='tableInfoVeh']/tbody/tr")
      for t2 in tableInfoVeh:
        td1 = t2.find_element_by_xpath("./td[1]").get_attribute("innerText") 
        td2 = t2.find_element_by_xpath("./td[2]").get_attribute("innerText") 
        ifile.write("<tr><td>" + td1 + "</td><td>" + td2 + "</td></tr>\n")
      ifile.write("</tbody></table>\n")
  ifile.write("</body></html>")
  ifile.close()
#=================================================

#-------------------------------------------------
def psa1paid():
  global PSA
  global login
  global passw
  
##  if PSA == None:
##    options = webdriver.ChromeOptions()
##    options.add_argument("--proxy-server=" + proxy)
##    PSA = webdriver.Chrome(options = options)
####################
##### check if location is UA    
####    PSA.get("https://2ip.ru/")
####    location = PSA.find_element_by_id("main-info-block").find_element_by_tag_name("a").get_attribute("innerText")
####    while location.find("Ukraine") + location.find("Украина")  == 0:
####      pass
##### and infinte loop if not
####################
##
##    PSA.get("http://public.servicebox.peugeot.com/")
##    PSA.add_cookie({"name": "PSACountry", "value": "GB"})
##    PSA.add_cookie({"name": "CodeLanguePaysOI", "value": "fr_FR"})
##
##    userid = PSA.find_element_by_name("userid")
##    userid.send_keys(login)
##    password = PSA.find_element_by_name("password")
##    password.send_keys(passw)
##    password.send_keys(Keys.RETURN)
##
##  else:
##    messagebox.showinfo(title=None, message="Already started")

  PSA = webdriver.Chrome()
  PSA.get("http://public.servicebox.peugeot.com/")

def psa2paid():
  global PSA
  global marque
  global pathDocs

  print("Init")
  marque = PSA.find_element_by_id("appTitle").get_attribute("innerText")
  if re.search("DS", marque) != None:
    marque = "docprDS"
  elif re.search("Citro.n", marque) != None:
    marque = "docprAC"
  elif re.search("Opel/Vauxhall", marque) != None:
    marque = "partsOV"
  elif re.search("Peugeot", marque) != None:
    marque = "docprAP"
  print(marque)
        
  infosVehicule = PSA.find_element_by_id("infosVehicule").get_attribute("innerText")
  VIN = PSA.find_element_by_id("short-vin").get_attribute("value")
  if VIN == "VIN/VIS":
      VIN = ""
  DownloadInit(infosVehicule + ("" if len(VIN) == 0 else (" " + VIN)) + "\\" )
  urlfilename = pathDocs + "DocsResourcesUrlList.txt"
  if os.path.isfile(urlfilename):
    urlfile = open(urlfilename, "w")
    urlfile.close()

  DocsUrlList = set(()) #tuples of all (url, filename)
  print("Start collecting docs urls")
  for docurllist in ["FCT0001", "FCT0100", "FCT0200", "FCT0300"]:
    file = open(pathMain + docurllist + "_url.txt", "r")
    print(f"...parsing {pathMain + docurllist}")
    for line in file:
      u = re.search("\((.*)\)", line).group(1).replace("'", "").replace(" ", "%20")
      url = callAction(u)
      filename = u.split(",")[4] + "-" + u.split(",")[0] + ".txt"
      DocsUrlList.add((url, filename))
    file.close()
  print("..........all docs urls are parsed")

  print(f"Start downloading and transforming docs")
  i = 1
  for url in DocsUrlList:
    print("...download doc " + str(i) + " of " + str(len(DocsUrlList)))
    DownloadFile(url[0], url[1], False)
    DocParseAndTransform(url[1]) #uses global pathDocs
    i = i + 1
  print("..........All resources are downloaded")
    
  print("Start collenting resources urls")
  DocsResourcesUrlList = set()  
  urlfile = open(urlfilename, "r")  
  for url in urlfile:
    DocsResourcesUrlList.add((url, ""))
    if re.search(r"btzoom.+\.gif", url) != None:
      DocsResourcesUrlList.add((url.replace(".gif", "_on.gif"), ""))
  urlfile.close()
  print("..........all urls are collected")

  print("Start downloading resources")
  i = 1
  for url in DocsResourcesUrlList:
    print("...download resource " + str(i) + " of " + str(len(DocsResourcesUrlList)))
    DownloadFile(url[0], "", False)
    i = i + 1
  print("..........All resources are downloaded")

  print("Gathering car info")
  getCarInfo()
  print("..........done")
  
  print("Now cleanup txt files")
  for p in [pathMain, pathMain + "docs\\"]:
    for f in os.listdir(p):
      if f.endswith(".txt"):
##         os.remove(p + f)
        pass
  print("..........now they're gone")


      
main()
