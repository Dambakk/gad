def prepareHTML(file, title):
	file.write("<!DOCTYPE html>")
	file.write("<html>")
	file.write("<head>")
	file.write("<title>HTML generator test</title>")
	file.write("</head>")
	file.write("<body>")	
	file.write("<h1>" + title + " </h1>" )

def endHTML(file):
	file.write("</body>")
	file.write("</html>")


def insertElement(type, content, color, x, y, w, h, file):
	file.write("<" + type )
	file.write(" style='background-color:" + color + "; margin-left:"+ str(x) + "px; margin-top:"+str(y) + "px;'" )
	file.write(" width='" + str(w) + "'" )
	file.write(" height='" + str(h) + "'" )
	file.write(">")
	file.write(content)
	file.write("</" + type + ">\n")