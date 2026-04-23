from time import sleep, time
from tkinter import *
import threading

# import web_scraping as ws biblioteca modificada

class App(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid()

        self.url = StringVar()
        self.tag = StringVar()
        self.attribute = StringVar()
        self.value = StringVar()
        self.driver_var = StringVar(value="chrome")
        self.driver_name = "chrome"
        self.msg = StringVar()

        # URL
        Label(self, text="URL:").grid(row=0 , column=0)
        self.url.set("")
        self.entry_url = Entry(self, textvariable=self.url)
        self.entry_url.grid(row=0 , column=1)

        # XPATH
        Label(self, text="Campo de análise:").grid(row=1 , column=0)

        Label(self, text="Tag:").grid(row=2 , column=0)
        self.entry_tag = Entry(self, textvariable=self.tag)
        self.entry_tag.grid(row=2 , column=1)

        Label(self, text="Atributo:").grid(row=3 , column=0)
        self.entry_attribute = Entry(self, textvariable=self.attribute)
        self.entry_attribute.grid(row=3 , column=1)

        Label(self, text="Valor:").grid(row=4 , column=0)
        self.entry_value = Entry(self, textvariable=self.value)
        self.entry_value.grid(row=4 , column=1)

        # Enter
        self.bind_all('<Key-Return>', self.print_contents)

        # Driver
        Label(self, text="Driver:").grid(row=5 , column=0)
        Radiobutton(self, text="Chrome", variable=self.driver_var, value="chrome", command=self.update_driver).grid(row=6 , column=1)
        Radiobutton(self, text="Edge", variable=self.driver_var, value="edge", command=self.update_driver).grid(row=7 , column=1)
        Radiobutton(self, text="Firefox", variable=self.driver_var, value="firefox", command=self.update_driver).grid(row=8 , column=1)

        # Buttons
        Button(self, text="Analisar", command=self.print_contents).grid(row=9 , column=0)
        Button(self, text="Sair", command=master.destroy).grid(row=10 , column=0)

        # Feedback
        self.msg.set("")
        Label(self, textvariable=self.msg, fg="red").grid(row=11, column=0, columnspan=2)

    def update_driver(self):
        self.driver_name = self.driver_var.get()

    def print_contents(self, event=None):
        error = self.validate_inputs()

        if error:
            self.msg.set(error)
            return

        self.msg.set("Analisando...")
        threading.Thread(target=self.scraping).start()

    def validate_inputs(self):
        url = self.url.get().strip()
        tag = self.tag.get().strip()
        attribute = self.attribute.get().strip()
        value = self.value.get().strip()

        if not url or url == "https://":
            return "Informe uma URL válida"
        if not url.startswith("http"):
            return "A URL deve começar com http ou https"
        if not tag:
            return "Informe a tag (ex: div, span)"
        if not attribute:
            return "Informe o atributo (ex: class, id)"
        if not value:
            return "Informe o valor do atributo"

        return None

    def scraping(self):
        url = self.url.get()
        xpath = f"//{self.tag.get()}[@{self.attribute.get()}='{self.value.get()}']"
        driver = self.driver_name

        try:
            field_value = "Deprecated" # ws.search(url, xpath, driver)
            if field_value == "Elemento não encontrado":
                result = field_value
            else:
                result = f"Valor encontrado: {field_value}"
        except Exception as e:
            result = f"Erro: {str(e)}"

        self.after(0, lambda: self.msg.set(result))

        print("URL:", url)
        print("Campo:", xpath)
        print("Driver:", driver)
        print("Valor:", field_value)

root = Tk()
icon = PhotoImage(file="boi_leilao.png")

app = App(root)
app.master.iconphoto(True, icon)
app.master.title("Visual Leilão")
app.master.geometry("720x480")
app.mainloop()