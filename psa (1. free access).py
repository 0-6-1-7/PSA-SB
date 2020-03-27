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
psaBrand = ""
pathMain = ""
##debug = 0
##proxy = "socks5://127.0.0.1:9150"
##login = "AN12345678"
##passw = "password"


def debugprint(s):
  if debug == 1:
    print(s)

def downloadImg(imgurl):
  cookies = PSA.get_cookies()
  rs = requests.Session()
  for cookie in cookies:
          rs.cookies.set(cookie['name'], cookie['value'])
  os.makedirs(pathMain + "files\\", exist_ok=True)
  imgstream = rs.get(imgurl, stream = True)
  imgfile = open(pathMain + "files\\" + os.path.basename(imgurl), "wb")
  imgstream.raw.decode_content = True
  shutil.copyfileobj(imgstream.raw, imgfile)
  imgfile.close()

def main():
  window = Tk()
  window.title("Free Servicebox")
  window.geometry('600x400')
  window.resizable(0, 0)
  window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoP.png'))
  window.call('wm', 'attributes', '.', '-topmost', True)

  dummyNW = Label().grid(column = 0, row = 0)
  dummySE = Label().grid(column = 5, row = 5)
  logoP = ImageTk.PhotoImage(file = "logoP.png")
  logoC = ImageTk.PhotoImage(file = "logoC.png")
  logoO = ImageTk.PhotoImage(file = "logoO.png")
  logoD = ImageTk.PhotoImage(file = "logoD.png")

  bP = Button(window, image = logoP, command=lambda: window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoP.png'))).grid(column = 1, row = 1)
  bC = Button(window, image = logoC, command=lambda: window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoC.png'))).grid(column = 2, row = 1)
  bO = Button(window, image = logoO, command=lambda: window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoO.png'))).grid(column = 3, row = 1)
  bD = Button(window, image = logoD, command=lambda: window.call('wm', 'iconphoto', window._w, ImageTk.PhotoImage(file='logoD.png'))).grid(column = 4, row = 1)

  go1 = Button(window, text = "Начинаем", command = psa1).grid(column = 1, row = 2)
  tt1 = Label(text = "В открывшемся окне браузера нужно:" + "\n" + \
              "1. авторизоваться и пройти капчу, если она появится;" + "\n" + \
              "2. ввести VIN или выбрать автомобиль и перейти\n     в раздел \"Каталог запасных частей\".").grid(sticky = "W", column = 2, row = 3, columnspan = 4)
  go2 = Button(window, text = "Продолжаем", command = psa2).grid(column = 1, row = 4)
   

  Grid.columnconfigure(window, 0, weight=1)
  Grid.columnconfigure(window, 5, weight=1)
  Grid.rowconfigure(window, 0, weight=1)
  Grid.rowconfigure(window, 2, weight=1)
  Grid.rowconfigure(window, 5, weight=1)

  window.mainloop()
  
def psa1():
  global PSA
  global login
  global passw
##  if PSA == None:
##    options = webdriver.ChromeOptions()
##    options.add_argument("--proxy-server=" + proxy)
##    PSA = webdriver.Chrome(options = options)
##    PSA.get("http://public.servicebox.peugeot.com/")
##    PSA.add_cookie({"name": "PSACountry", "value": "GB"})
##    PSA.add_cookie({"name": "CodeLanguePaysOI", "value": "fr_FR"})
##    userid = PSA.find_element_by_name("userid")
##    userid.send_keys(login)
##    password = PSA.find_element_by_name("password")
##    password.send_keys(passw)
##    password.send_keys(Keys.RETURN)
##  else:
##    messagebox.showinfo(title=None, message="Already started")

  PSA = webdriver.Chrome()
  PSA.get("http://public.servicebox.peugeot.com/")


def psa2():
  global PSA
  global pathMain
  if PSA == None:
    tkinter.messagebox.showwarning(title=None, message="No main window")
    return
  try:
    PSA.find_elements_by_class_name("highlight first")
  except:
    tkinter.messagebox.showwarning(title=None, message="Site not ready")
    return

  for x in ["FCT0001", "FCT0100", "FCT0200", "FCT0300"]:
    xt = PSA.find_element_by_xpath("//*[@id='menu_" + x + "']/a")
    PSA.execute_script("arguments[0].click();", xt)
    time.sleep(2)

    infosVehicule = PSA.find_element_by_id("infosVehicule").get_attribute("innerText")
    VIN = PSA.find_element_by_id("short-vin").get_attribute("value")
    pathMain = "SB\\" + infosVehicule + ("" if VIN == "VIN/VIS" else (" " + VIN)) + "\\" 
    os.makedirs(pathMain, exist_ok = True)
    ftxt = open(pathMain + x + ".txt", "w")
    furl = open(pathMain + x + "_url.txt", "w")
    ftxt.write(infosVehicule + " " + ("" if VIN == "VIN/VIS" else (" $" + VIN)) + "\n")
    ftxt.flush()

    for y in PSA.find_elements_by_xpath("//*[@id='listingtype']/li"):
      yt = y.find_element_by_xpath(".//h4").get_attribute("title")
      yi = y.find_element_by_xpath(".//img").get_attribute("src")
      ftxt.write("[H4]; " + yt + "; " + os.path.basename(yi) + "\n")
      ftxt.flush()
      downloadImg(yi)
      ZZZ = y.find_elements_by_xpath(".//ul/li")
      for z in ZZZ:
        zt = z.find_element_by_xpath(".//a")
        if re.match("http", zt.get_attribute("href")) == None: #пропустим мёртвые разделы типа "Персонализация торможения"
          sid =re.search(r"\"(.*?)\",\"(.*?)\"", zt.get_attribute("href")) #get both ids from href: javascript:afficheAjaxTabRecapDoc("FCT0049","FCT0512",false)
          ftxt.write("[H5]; " + \
                  sid.group(2) + "-" + sid.group(1) + "; " + \
                  zt.get_attribute("title") + "\n")
          PSA.execute_script("arguments[0].click();", zt)
          try:
            tableheader = WebDriverWait(PSA, 10).until(EC.presence_of_element_located((By.ID, ("ongletTypeDoc"))))
          except:
            PSA.quit()
          DDDn = int(re.search("((\d+))", tableheader.get_attribute("innerText")).group(0))
          if DDDn > 0:
            try:
              wait = WebDriverWait(PSA, 10).until(EC.presence_of_element_located((By.ID, ("line" + str(DDDn-1)))))
            except:
              pass

            for DDD in range(0, DDDn):
              d = PSA.find_element_by_xpath("//*[@id='line" + str(DDD )+ "']")
              onclickurl = re.search(r"(callAction\(.*\))", d.get_attribute("onclick")).group(1)
              tid = re.search(r"\(\'(.*?)\',\'(.*?)\',\'(.*?)\',\'(.*?)\',\'(.*?)\'", onclickurl)
              ftxt.write("[D]; " + \
                      tid.group(5) + "-" + tid.group(1) + "; " + \
                      d.find_element_by_xpath(".//td[1]").get_attribute("innerText") + "; " + \
                      d.find_element_by_xpath(".//td[2]").get_attribute("innerText") + "; " + \
                      d.find_element_by_xpath(".//td[3]").get_attribute("innerText") + "; " +
                      onclickurl + "\n")
              ftxt.flush()
              furl.write("[doc]; " + onclickurl + "\n")
              furl.flush()
          else:
            ftxt.write("[D]; nodocs\n")
            ftxt.flush()
        else:
          pass
    ftxt.close()
    furl.close()
	
  print("1st step complete")

  print("2nd step started")
  for x in ["FCT0001", "FCT0100", "FCT0200", "FCT0300"]:
    fin = open(pathMain + x + ".txt", "r")
    fout = open(pathMain + x + ".html", "w")
    NameVin = fin.readline()
    fout.write("<html>" + "\n")
    fout.write("<head>" + "\n")
    fout.write("<link href=\"files/main.css\" rel=\"stylesheet\" type=\"text/css\" media=\"all\">" + "\n")
    fout.write("<script src=\"files/script.js\"></script>" + "\n")
    fout.write("<title>Service Box</title>" + "\n")
    fout.write("</head>" + "\n")
    fout.write("<body>" + "\n")

    s = NameVin.split("$")
    if len(s) == 2:
      fout.write("<h1>" + s[0] + " <a href='" + s[1] + ".html' target='_blank'>" + s[1] + "</a>" + "</h1>" + "\n")
    else:
      fout.write("<h1>" + NameVin + "</h1>" + "\n")
    fout.write("<div class=\"sidebar\">" + "\n")
    fout.write("<ul>" + "\n")
    menuactive = lambda s: "class=\"active\" " if s == x else ""
    fout.write("<li " + menuactive("FCT0001") + "id=\"FCT0001\"><a href=\"FCT0001.html\">Слесарные работы</a></li>" + "\n")
    fout.write("<li " + menuactive("FCT0100") + "id=\"FCT0100\"><a href=\"FCT0100.html\">Кузовные работы</a></li>" + "\n")
    fout.write("<li " + menuactive("FCT0200") + "id=\"FCT0200\"><a href=\"FCT0200.html\">Оборудование</a></li>" + "\n")
    fout.write("<li " + menuactive("FCT0300") + "id=\"FCT0300\"><a href=\"FCT0300.html\">Электрооборудование</a></li>" + "\n")
    fout.write("</ul>" + "\n")
    fout.write("</div>" + "\n")
    fout.write("<div class=\"content\">" + "\n")
    fout.flush()

    H4open = 0
    DLopen = 0
    l = "" #will store all listings
    docs = "" #will store all docs
    nodocs = set(()) #set of FCTs with no docs
    
    for line in fin:
      sss = line.strip(" \n").split(";")
      s0 = sss[0].strip("[] ")
      if s0 == "H4":
        if H4open == 1:
          if DLopen == 1:
            docs = docs + ("</tbody></table>\n</div>\n")                   
            DLopen = 0
          l = l + "</ul>" + "\n"
          H4open = 0
        if H4open == 0:
          #[H4]; Двигатель; http://public.servicebox.peugeot.com/docprAC/resources/4.34.4/AC/image/fonction/Fct20091028113400134.jpg
          l = l + "<ul class=\"listingtype\"><h4><img src=" + \
                  "\"files/" + sss[2].strip(" ") + "\" align=\"left\">" + \
                  "&nbsp;&nbsp;&nbsp;" + sss[1].strip(" ") + "</h4>" + "\n"
          H4open = 1
      elif s0 == "H5":
        #[H5]; FCT0049, БЛОК ДВИГАТЕЛЯ
        FCT = sss[1].strip(" ")
        if DLopen == 1:
          docs = docs + ("</tbody></table>\n</div>\n")                   
          DLopen = 0
        l = l + "<li id=\"" + FCT + "\" onclick = \"doclist(this.id)\">&nbsp;" + sss[2].strip(" ") + "&nbsp;</li>" + "\n"

      elif s0 == "D":
        if sss[1].strip(" ") == "nodocs":
          nodocs.add(FCT)
          docs = docs + "<div class=\"doclist nodocs\" id=\"" + FCT + "docs\">В этом разделе нет документов</div>\n"
        else:
          if DLopen == 0:
            #[D]; ZZZZZZZZZZZZ; ДВИГАТЕЛЬ; use=ВПРЫСК EC5F 85КВТ;;callAction...
            docs = docs + "<div class=\"doclist\" id=\"" + FCT + "docs\">\n"
            docs = docs + ("<table><thead><tr><th>Название</th><th>Применение</th><th>Поставщик</th></tr></thead><tbody>" + "\n")
            DLopen = 1           
          if DLopen == 1:
            docs = docs + ("<tr onclick=\"javascript: window.open(\'docs/" + sss[1].strip(" ") + ".html\');\"><td>" + sss[2].strip(" ")+"</td><td>" + sss[3].strip(" ") + "</td><td></td></tr>" + "\n")
    #end of for loop for lines
    fin.close()
    if DLopen == 1:
      docs = docs + ("</tbody></table>\n</div>\n")                   
    if H4open == 1:
      l = l + "</ul>" + "\n"
    #find all FCT with no docs and add 'nodocs' style
    for fct in nodocs:
      s = "<li id=\"" + fct + "\""
      t = re.search(s, l)
      if t != None:
        l = l.replace(s, "<li class=\"nodocs\" id=\"" + fct + "\"")
    fout.write(l)
    fout.write(docs)
    fout.write("</div>\n</body>\n</html>")
    fout.close()
  # end of loop for files
  print("2nd step complete")

  print("copy common files")
  pathCF = os.path.abspath(pathMain + "..\\..\\common files\\files")
  for f in os.listdir(pathCF):
    shutil.copy(os.path.join(pathCF, f), pathMain + "files")
  print("..........all done")
main()
