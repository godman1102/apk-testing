from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from urllib.request import urlopen
from datetime import datetime
import json, requests, os

def get_data(filename:str="manager_database.json"):
    with open(filename, "r") as f:
        config = json.load(f)
    return config

class Data:
    version = "v1.0.0"
    user_ip = None
    if os.path.isfile("manager_database.json"):
        save_file = get_data()
    else:
        save_item = {
            "remembered_user": None,
            "remembered_password": None,
            "remember_me": False,
            "background_image_path": "tumblr_dbfbdccf88850675ecc7ae6aec2a01fb_931fd4ee_540.gif",
            "users": []
        }
        with open("manager_database.json", "w") as f:
            json.dump(save_item, f, indent=4)
        save_data = get_data()
    account_index = 0

    def get_user_ip():
        try:
            return str(urlopen("https://api.ipify.org").read().decode().strip())
        except:
            return None

    def install(url:str):
        req = requests.get(url)
        filename = req.url[url.rfind("/")+1:]
        with open(filename, "wb") as f:
            for chunk in req.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return filename

    def get_time(year:bool=False):
        ct = datetime.now().strftime("%I:%M %p")
        if ct.startswith("0"):
            ct = ct[1:]
        if year is True:
            yt = datetime.now().strftime("%d/%m/%Y")
            return yt + " " + ct
        return ct

def save_data(filename:str="manager_database.json", object:dict=Data.save_file):
    with open(filename, "w") as f:
        json.dump(object, f, indent=4)

Builder.load_string(""" 
<LoginScreen>:
    Image:
        source: 'tumblr_dbfbdccf88850675ecc7ae6aec2a01fb_931fd4ee_540.gif'
        allow_stretch: True

    BoxLayout:
        orientation: 'vertical'
        padding: 10

        BoxLayout:
            orientation: 'vertical'
            pos_hint: {'top': 1}
                            
            TextInput:
                id: login_username_entry
                multiline: False
                hint_text: 'Username'
                size_hint_x: 1
                size_hint_y: 0.3
            
            TextInput:
                id: login_password_entry
                multiline: False
                password: True
                hint_text: 'Password'
                size_hint_x: 1
                size_hint_y: 0.3
                            
        BoxLayout:
            orientation: 'horizontal'
            pos_hint: {'top': 1}

            CheckBox:
                on_press: root.remember_me(self)
                id: login_check_box
                size_hint_x: 0.25
                size_hint_y: 0.25

            Button:
                text: 'Login'
                on_press: root.validate_credentails()
                size_hint_x: 0.5
                size_hint_y: 0.3
                            
            Button:
                text: 'Add Account'
                on_press: root.create_account()
                size_hint_x: 0.5
                size_hint_y: 0.3

        Label:
            id: login_error_label
            text: ''

<PasswordScreen>:
    Image:
        source: 'tumblr_dbfbdccf88850675ecc7ae6aec2a01fb_931fd4ee_540.gif'
        allow_stretch: True
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10

        BoxLayout:
            orientation: 'vertical'

            TextInput:
                id: username_input
                multiline: False
                hint_text: 'Username'
                size_hint_x: 1
                size_hint_y: 0.3

            TextInput:
                id: password_input
                multiline: False
                password: True
                hint_text: 'Password'
                size_hint_x: 1
                size_hint_y: 0.3

            TextInput:
                id: service_input
                multiline: False
                hint_text: 'Service'
                size_hint_x: 1
                size_hint_y: 0.3

        BoxLayout:
            orientation: 'horizontal'

            Button:
                text: 'Add Account'
                on_press: root.add_item()
                size_hint_x: 0.5
                size_hint_y: 0.3

            Button:
                text: 'Delete Account'
                on_press: root.delete_account()
                size_hint_x: 0.5
                size_hint_y: 0.3

        ListWidget:
            viewclass: 'Label'
            orientation: 'vertical'
            id: listview_output
            
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 0.4, None
                size_hint_y: None
                height: self.minimum_height
                oreintation: 'vertical'

<ScreenManagement>:
    LoginScreen:
        name: 'login_screen'
    PasswordScreen:
        name: 'password_screen'
""")

class LoginScreen(Screen):
    def validate_credentails(self):
        username = self.ids.login_username_entry.text
        password = self.ids.login_password_entry.text
        Data.account_index = 0
        account_found = False
        for account in Data.save_file['users']:
            if account['username'] == username and account['password'] == password:
                account_found = True
                break
            Data.account_index += 1
        if account_found is False:
            self.ids.login_error_label.text = "Failed to find account, try a different username or password"
            self.ids.login_username_entry.text = ""
            self.ids.login_password_entry.text = ""
            return
        self.switch_password_screen(self)

    def switch_password_screen(self, screen):
        self.manager.transition.direction = "up"
        self.manager.current = 'PasswordScreen'

    def remember_me(self, screen):
        if self.ids.login_check_box.state == "normal":
            Data.save_file['remember_me'] = False
            save_data()
        elif self.ids.login_check_box.state == "down":
            Data.save_file['remember_me'] = True
            save_data()

    def check_remember_me(self):
        found_account = False
        if Data.save_file['remember_me'] is True:
            for account in Data.save_file['users']:
                if account['username'] == Data.save_file['remembered_user'] and account['password'] == Data.save_file['remembered_password']:
                    self.ids.login_check_box.state = True
                    break
            if found_account is True:
                self.ids.login_check_box.state = True
                self.ids.login_username_entry.text = Data.save_file['remembered_username']
                self.ids.login_password_entry.text = Data.save_file['remembered_password']
            else:
                Data.save_file['remembered_username'] = None
                Data.save_file['remembered_password'] = None
                save_data()

    def create_account(self):
        username = self.ids.login_username_entry.text
        password = self.ids.login_password_entry.text
        account_found = False
        for account in Data.save_file['users']:
            if account['username'] == username and account['password'] == password:
                account_found = True
                break
        if account_found is True:
            self.ids.login_error_label.text = "Failed to create account because it already exists"
        user_item  = {"username": username, "password": password, "saved_passwords": []}
        Data.save_file['users'].append(user_item)
        save_data()
        self.ids.login_error_label.text = "Created an Account, you can now sign into it :)"

class PasswordScreen(Screen):
    class ListWidget(RecycleView):
        account = Data.save_file['users'][Data.account_index]

        def add_item(self):
            formatted = f"{self.account['username']} - {self.account['password']} - {self.account['service']}"
            self.data.append({"text": formatted})

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            data = []
            for user in self.account['saved_passwords']:
                formatted = f"{user['username']} - {user['password']} - {user['service']}"
                data.append({"text": formatted})
            self.data = data

    def add_account(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        service = self.ids.service_input.text

    def delete_account(self):
        pass

class ScreenManagement(ScreenManager):
    def __init__(self):
        super().__init__()

        self.add_widget(LoginScreen(name="LoginScreen"))
        self.add_widget(PasswordScreen(name="PasswordScreen"))

class MainApp(App):
    def build(self):
        return ScreenManagement()

if os.path.isfile("tumblr_dbfbdccf88850675ecc7ae6aec2a01fb_931fd4ee_540.gif") is False:
    Data.install("https://media.discordapp.net/attachments/1117266223055511552/1172701422492602448/tumblr_dbfbdccf88850675ecc7ae6aec2a01fb_931fd4ee_540.gif")
MainApp().run()