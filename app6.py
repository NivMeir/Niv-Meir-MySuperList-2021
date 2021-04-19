"""
Niv Meir
python 3.8
"""


from flask import Flask, render_template, request, redirect, url_for, flash, session
import DataBase
import emails_and_encryption
import super_maps

app = Flask(__name__)
app.secret_key = "SuperList"
extra = emails_and_encryption.Extras()
mymap = super_maps.Maps()
users = DataBase.Users()
mylist = DataBase.Mylist()
allproducts = DataBase.Allproducts()
global productlist
productlist = ["", "Fruits and Vegetables", "Drinks", "Meat, Chicken and Fish", "Bread", "Milk, Cheese and Eggs", "Snacks"]

@app.route("/", methods = ["GET"])
def start():
    """
    send the login page to the user
    rtype: html page
    """
    return render_template("login.html")


#must be more then 8 chars, letters and numbers
def pass_check(password):
    """
    check the password, it has to be more then 8 chars, letters and numbers
    param password: the user password that he want to register with
    type: string
    return: checks that the password received is conditional
    rtype: boolean
    """
    if len(password) < 8:
        return False
    letter = False
    number = False
    for char in password:
        if str.isalpha(char):
            letter = True
        elif str.isalnum(char):
            number = True
    return letter and number


@app.route("/register", methods = ["GET", "POST"])
def register():
    """
    GET:
    retrun the register page
    rtype: html page
    POST:
    get the user information and write them at the database if they meet the requirements
    return the register page if the information from the user is incorrect, otherwise return the path to the next page
    rtype: html page or url path
    """
    if request.method == 'GET':
        return render_template("register.html")
    else:
        try:
            name = request.form.get("name")
            password = request.form.get("password")
            email = request.form.get("email")
            if users.email_isexist(email):
                flash("The Email Is Already In The System")
                return render_template("register.html")
            elif not pass_check(password):
                flash("The Password Must Have 8 Chars, Letters And Numbers")
                return render_template("register.html")
            elif len(name) > 10 or len(name) < 2:
                flash("Your Name Has To Be Between 2 Chars To 10!")
                return render_template("register.html")
            encryptpass = extra.encrypt(password)
            users.insert_user(email, encryptpass, name)
            userid = users.get_user_id(email)
            session['userid'] = userid
            return redirect(url_for('main'))
        except:
            return render_template("register.html")

@app.route("/login", methods = ["POST"])
def login():
    """
        get the user information and check them at the database if they meet the requirements
        return the login page if the information from the user is incorrect, otherwise return the path to the next page
        rtype: html page or url path
        """
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        #email = "nivmeir2804@gmail.com"
        #password = "hamagniv28"
        if not users.user_isexist(email, password):
            flash('User was not found!')
            return render_template("login.html")
        userid = users.get_user_id(email)
        session['userid'] = userid
        return redirect(url_for('main'))
    except:
        return render_template("login.html")


@app.route("/forgotpass", methods = ["GET", "POST"])
def forgotpass():
    """
        GET:
        retrun the forgotpass page
        rtype: html page
        POST:
        get the user's email and check it at the database if it exist, and then send a code to their email
        return the forgotpass page if the information from the user is incorrect, otherwise return the path to the next page
        rtype: html page or url path
        """
    if request.method == 'GET':
        return render_template("forgotpass.html")
    elif request.method == 'POST':
        try:
            email = request.form.get("email")
            if email != None and users.email_isexist(email):
                session["userid"] = users.get_user_id(email)
                code = extra.codegenerator()
                session["code"] = code
                extra.send_email(email, code)
                return redirect(url_for('mailcode'))
            else:
                flash("Email Was Not Found")
                return render_template("forgotpass.html")
        except:
            return render_template("forgotpass.html")
    else:
        print("done forgot password")


@app.route("/mailcode", methods=["GET", "POST"])
def mailcode():
    """
    GET:
    retrun the mailcode page
    rtype: html page
    POST:
    get the user's code and check it
    return the forgotpass page if the code from the user is incorrect, otherwise return the path to the next page
    rtype: html page or url path
    """
    if request.method == 'GET':
        return render_template("mailcode.html")
    elif request.method == 'POST':
        try:
            code = request.form.get("code")
            if code != None and code == session["code"]:
                return redirect(url_for('changepassword'))
            else:
                flash("Wrong Code")
                return render_template("mailcode.html")
        except:
            return render_template("mailcode.html")
    else:
        print("done mail code")



@app.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    """
    GET:
    retrun the changepassword page
    rtype: html page
    POST:
    get the user's new password, if it meet the requirements the password is changing at the database
    return the changepassword page if the password from the user is incorrect, otherwise return the path to the next page
    rtype: html page or url path
    """
    if request.method == 'GET':
        return render_template("changepassword.html")
    elif request.method == 'POST':
        try:
            newpass = request.form.get("newpass")
            email = users.get_user_email(session["userid"])
            if newpass != None and pass_check(newpass):
                encryptpass = extra.encrypt(newpass)
                users.update_password(email, encryptpass)
                return redirect(url_for('main'))
            else:
                flash("The Password Must Have 8 Chars, Letters And Numbers")
                return render_template("changepassword.html")
        except:
            print("something went wrong")
            return render_template("changepassword.html")
    else:
        print("done change password")


@app.route("/main", methods = ["GET"])
def main():
    """
    retrun the main page
    rtype: html page
    """
    id = ''
    if 'userid' in session:
        id = session['userid']
    name = users.get_user_name(id)
    return render_template("main.html", name=name)


@app.route("/usermap", methods = ["GET"])
def showmap():
    """
    retrun the usermap page with the user map
    rtype: html page
    """
    import random
    if request.method == 'GET':
        place = mylist.get_place(session["userid"])
        filename = "/" + str(session["userid"])+ str(random.randint(1000, 9999)) + ".jpg"
        print("#filename " + filename)
        mymap.draw_arrows(place, filename)
        path = "user_maps" + filename
        web_param = {'path': path, 'imgheight': 500, 'imgwidth': 890}
        #path = r"static\user_maps" + filename
        return render_template("usermap.html", **web_param)

@app.route("/mysuperlist", methods = ["GET"])
def my_list():
    """
    retrun the mysuperlist page with the users list
    rtype: html page
    """
    if request.method == 'GET':
        data = mylist.get_my_products(session["userid"])
        return render_template("mysuperlist.html", data=data)

@app.route("/mysuperlist/delete/<product>", methods = ["GET"])
def delete_product(product):
    """
    param: the product's name we want to delete
    ptype: string

    return the url of mysuperlist page after deleting a product
    rtype: url
    """
    if request.method == 'GET':
        mylist.delete_product(product, session['userid'])
        flash(product + " Has Been Deleted From Your Super List")
    return redirect('/mysuperlist')

def get_location_num(locatuonname):
    for i in range(len(productlist)):
        if locatuonname == productlist[i]:
            return i

def insertproducts():
    allproducts.insert_product("apple", 'A', get_location_num("Fruits and Vegetables"),"Fruits and Vegetables" )
    allproducts.insert_product("banana", 'A', get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("orange", 'A', get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("strawberry", 'B', get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("grapes", 'B', get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("watermelon", 'B', get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("potato", 'C',get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("onion", 'C',get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("tomato", 'C',get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("cucumber", 'C',get_location_num("Fruits and Vegetables"), "Fruits and Vegetables")
    allproducts.insert_product("coca cola", 'A',get_location_num("Drinks"), "Drinks")
    allproducts.insert_product("sprite", 'A',get_location_num("Drinks"), "Drinks")
    allproducts.insert_product("fanta", 'B',get_location_num("Drinks"), "Drinks")
    allproducts.insert_product("orange juice", 'B',get_location_num("Drinks"), "Drinks")
    allproducts.insert_product("beer", 'C',get_location_num("Drinks"), "Drinks")
    allproducts.insert_product("red wine", 'C',get_location_num("Drinks"), "Drinks")
    allproducts.insert_product("water", 'D',get_location_num("Drinks"), "Drinks")
    allproducts.insert_product("white wine", 'D',get_location_num("Drinks"), "Drinks")
    allproducts.insert_product("bakala fish", 'A',get_location_num("Meat, Chicken and Fish"), "Meat, Chicken and Fish")
    allproducts.insert_product("salmon", 'A',get_location_num("Meat, Chicken and Fish"), "Meat, Chicken and Fish")
    allproducts.insert_product("chicken Breast", 'A',get_location_num("Meat, Chicken and Fish"), "Meat, Chicken and Fish")
    allproducts.insert_product("chicken thighs", 'B',get_location_num("Meat, Chicken and Fish"), "Meat, Chicken and Fish")
    allproducts.insert_product("entrecote", 'B',get_location_num("Meat, Chicken and Fish"), "Meat, Chicken and Fish")
    allproducts.insert_product("ground beef", 'B',get_location_num("Meat, Chicken and Fish"), "Meat, Chicken and Fish")
    allproducts.insert_product("sausage", 'B',get_location_num("Meat, Chicken and Fish"), "Meat, Chicken and Fish")
    allproducts.insert_product("pita", 'A',get_location_num("Bread"), "Bread")
    allproducts.insert_product("bread", 'A',get_location_num("Bread"), "Bread")
    allproducts.insert_product("cream cheese", 'A',get_location_num("Milk, Cheese and Eggs"), "Milk, Cheese and Eggs")
    allproducts.insert_product("yellow cheese", 'A',get_location_num("Milk, Cheese and Eggs"), "Milk, Cheese and Eggs")
    allproducts.insert_product("yogurt", 'B',get_location_num("Milk, Cheese and Eggs"), "Milk, Cheese and Eggs")
    allproducts.insert_product("mozzarella cheese", 'B',get_location_num("Milk, Cheese and Eggs"), "Milk, Cheese and Eggs")
    allproducts.insert_product("cottage cheese", 'C',get_location_num("Milk, Cheese and Eggs"), "Milk, Cheese and Eggs")
    allproducts.insert_product("eggs", 'C',get_location_num("Milk, Cheese and Eggs"), "Milk, Cheese and Eggs")
    allproducts.insert_product("milk", 'C',get_location_num("Milk, Cheese and Eggs"), "Milk, Cheese and Eggs")
    allproducts.insert_product("bamba", 'A',get_location_num("Snacks"), "Snacks")
    allproducts.insert_product("chips", 'A',get_location_num("Snacks"), "Snacks")
    allproducts.insert_product("pretzels", 'B',get_location_num("Snacks"), "Snacks")
    allproducts.insert_product("cornflaxes", 'B',get_location_num("Snacks"), "Snacks")

@app.route("/allproductsmenu", methods = ["GET"])
def all_products_menu():
    """
    retrun the mainproducts page with the possible departments
    rtype: html page
    """
    if request.method == "GET":
        if allproducts.isempty():
            insertproducts()
        return render_template("mainproducts.html")

@app.route("/allproductsmenu/<department>", methods = ["GET"])
def choose_department(department):
    """
   param: the department's name the user chose
   ptype: string

   return the allproducts page with the department the user chose or with the product the user searched for
   rtype: html page
   """
    if request.method == 'GET':
        data = allproducts.get_products(department)
        search = ""
        try:
            search = request.args.get("search")
        except:
            print("Wasn't Found")
        if search != None:
            data = allproducts.get_products(search)
        return render_template("allproducts.html", data=data)

@app.route("/allproductsmenu/<department>/insert/<product>", methods = ["GET", "POST"])
def insert_products(department, product):
    """
       param: the department's name the user chose
       ptype: string

       param: the product he want to add to his list
       ptype: string

       return the url of allproductsmenu by the chosen department page after adding thr chosen product
       rtype: url
       """
    if request.method == 'GET':
        info = allproducts.get_product_info(product)
        if info != False:
            mylist.insert_product(info[0], info[2], info[1], info[3], session['userid'])
            flash(product + " Has Been Added To Your Super List")
        else:
            print("the product was not found")
        url = '/allproductsmenu/' + str(department)
        return redirect(url)


if __name__ == '__main__':
    app.run(port= 80)
    #host='0.0.0.0' להתחברות ממכשירים אחרים אחרת לפחות מהפקודה למעלה