from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from decimal import *
import Pyro5.api
from kivy.config import Config

from kivy.uix.widget import Widget

getcontext().prec = 13 + 4
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable the right click red dot


def popupError(String):
    app = App.get_running_app()
    popuperror = Popup(title='Error', content=Label(text=String), size_hint=(None, None),
                       size=(app.root.width / 2, app.root.height / 2))
    popuperror.open()


class AuthPage(Screen):
    def __init__(self, **kwargs):
        super(AuthPage, self).__init__(**kwargs)
        self.authCode = None

    def auth(self, name, pin):
        try:
            atm = Pyro5.api.Proxy("PYRONAME:example.Atm")
            self.authCode = atm.Auth(pin, name)
            if self.authCode == "Invalid credentials" or self.authCode == "backend error":
                popupError(self.authCode)
            else:
                self.manager.current = 'choose'
                self.manager.get_screen('choose').updateBalance()
        except Pyro5.errors.NamingError:
            popupError("Server is offline")

    def getAuthCode(self):
        return self.authCode


class ChoosePage(Screen):
    def updateBalance(self):
        try:
            atm = Pyro5.api.Proxy("PYRONAME:example.Atm")
            authCode = self.manager.get_screen('auth').getAuthCode()
            money = Decimal(atm.getBalance(authCode))
            money = round(money, 2)
            self.ids.balance.text = str(money)
        except Pyro5.errors.NamingError:
            popupError("Server is offline")
    def withdraw(self):
        #change to withdraw page and pass authcode
        self.manager.current = 'withdraw'

    def deposit(self):
        self.manager.current = 'deposit'




class WithdrawPage(Screen):
    def withdraw(self, value):
        try:
            atm = Pyro5.api.Proxy("PYRONAME:example.Atm")
            money = Decimal(value)
            authCode = self.manager.get_screen('auth').getAuthCode()
            answer = atm.withdraw(authCode, money)
            if answer == "Success":
                self.manager.current = 'choose'
                self.manager.get_screen('choose').updateBalance()
            else:
                popupError(answer)
        except Pyro5.errors.NamingError:
            popupError("Server is offline")

    def back(self):
        self.manager.current = 'choose'
        self.manager.get_screen('choose').updateBalance()

class DepositPage(Screen):
    def deposit(self, value):
        try:
            atm = Pyro5.api.Proxy("PYRONAME:example.Atm")
            money = Decimal(value)
            authCode = self.manager.get_screen('auth').getAuthCode()
            answer = atm.deposit(authCode, money)
            if answer == "Success":
                self.manager.current = 'choose'
                self.manager.get_screen('choose').updateBalance()
            else:
                popupError(answer)
        except Pyro5.errors.NamingError:
            popupError("Server is offline")

    def back(self):
        self.manager.current = 'choose'
        self.manager.get_screen('choose').updateBalance()

class AtmApp(App):
    def build(self):
        sm = ScreenManager()
        screen1 = AuthPage()
        screen2 = ChoosePage()
        screen3 = WithdrawPage()
        screen4 = DepositPage()
        sm.add_widget(screen1)
        sm.add_widget(screen2)
        sm.add_widget(screen3)
        sm.add_widget(screen4)
        return sm


if __name__ == '__main__':
    AtmApp().run()
