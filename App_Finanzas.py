import tkinter as tk
from tkinter import ttk, messagebox, Label
from threading import Thread
import ccxt
import requests

class CurrencyRatesUpdater:
    def __init__(self):
        self.base_url = "https://open.er-api.com/v6/latest/"
        self.base_currency = "DOP"
        self.exchange_rates = {}

    def fetch_exchange_rates(self):
        try:
            response = requests.get(f"{self.base_url}{self.base_currency}")
            data = response.json()
            self.exchange_rates = data["rates"]
        except Exception as e:
            print(f"Error al recuperar los tipos de cambio: {e}")

    def get_equivalent_in_dop(self, currency_code, amount):
        if not self.exchange_rates:
            self.fetch_exchange_rates()

        try:
            rate = self.exchange_rates[currency_code]
            equivalent_in_dop = amount / rate
            return round(equivalent_in_dop, 2)
        except KeyError:
            return "Codigo de moneda no valido"
        except Exception as e:
            return f"Error: {e}"

class FinanzasApp:
    symbols = ['MSFT', 'AAPL', 'NVDA', 'AMZN', 'GOOGL']

    def __init__(self, root):
        self.root = root
        self.root.title("Finanzas en Tiempo Real")

        # Configura las opciones
        self.options = ["Divisas", "Bolsa", "Criptomonedas"]

        # Variable para rastrear la opción seleccionada
        self.selected_option = tk.StringVar(value=self.options[0])  # Predeterminado: "Divisas"

        # Contenedor para los botones de sección
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # Configura los botones para cambiar de secciones
        for option in self.options:
            ttk.Button(self.button_frame, text=option, command=lambda o=option: self.select_option(o)).pack(side=tk.LEFT, padx=5, pady=5)

        # Inicializa el contenido de la sección seleccionada
        self.initialize_section()

        # Configura la conexión con el exchange (Binance)
        self.exchange = ccxt.binance()

        # Almacena las etiquetas de resultados en un diccionario
        self.result_labels = {}

        # Inicia la actualización automática en tiempo real
        self.update_interval = 1000  # Actualización cada 1000 milisegundos (1 segundo)
        self.root.after(self.update_interval, self.update_data)

        # Instancia de CurrencyRatesUpdater
        self.rates_updater = CurrencyRatesUpdater()

    def select_option(self, option):
        self.selected_option.set(option)
        self.initialize_section()

    def initialize_section(self):
        # Elimina los widgets existentes
        for widget in self.root.winfo_children():
            if widget not in [self.root.nametowidget("."), self.button_frame]:
                widget.destroy()

        # Inicializa el diccionario de etiquetas de resultados
        self.result_labels = {}

        # Obtén la opción seleccionada
        selected_option = self.selected_option.get()

        # Configura el contenido según la opción seleccionada
        if selected_option == "Criptomonedas":
            # Código de la sección de Criptomonedas
            self.create_crypto_label("BTC/USDT")
            self.create_crypto_label("ETH/USDT")
            self.create_crypto_label("BNB/USDT")
            self.create_crypto_label("SOL/USDT")
            self.create_crypto_label("XRP/USDT")

        elif selected_option == "Divisas":
            # Configura el contenido de la sección de Divisas
            self.create_currency_rates_widgets()
            self.create_currency_converter_widgets()

        elif selected_option == "Bolsa":
            # Configura el contenido de la sección de Bolsa
            self.create_stock_labels()

    def create_crypto_label(self, symbol):
        # Crea las etiquetas para mostrar la información de las criptomonedas
        label = ttk.Label(self.root, text=symbol, font=("Arial", 12, "bold"))
        result_label = ttk.Label(self.root, text="", font=("Arial", 10))
        
        label.pack(pady=5)
        result_label.pack(pady=5)

        # Almacena la referencia de la etiqueta de resultados en un diccionario
        self.result_labels[symbol] = result_label

    def create_currency_rates_widgets(self):
        self.currency_labels = {
            "USD": tk.StringVar(),
            "EUR": tk.StringVar(),
            "CNY": tk.StringVar(),
            "GBP": tk.StringVar(),
            "CHF": tk.StringVar(),
            "JPY": tk.StringVar()
        }

        currency_names_es = {
            "USD": "Dólar Estadounidense",
            "EUR": "Euro",
            "CNY": "Yuan Chino",
            "GBP": "Libra Esterlina",
            "CHF": "Franco Suizo",
            "JPY": "Yen Japonés"
        }

        for i, (currency, label_var) in enumerate(self.currency_labels.items()):
            tk.Label(self.root, text=f"1 {currency} ({currency_names_es[currency]}) a DOP:", font=("Arial", 10, "bold")).pack(pady=5)
            ttk.Label(self.root, textvariable=label_var).pack(pady=5)

    def create_currency_converter_widgets(self):
        converter_frame = ttk.Frame(self.root, padding="10")
        converter_frame.pack(pady=10)

        tk.Label(converter_frame, text="Moneda", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        self.selected_currency = tk.StringVar(value="USD")  # Establecer USD como valor predeterminado
        self.currency_combobox = ttk.Combobox(converter_frame, values=list(self.currency_labels.keys()), textvariable=self.selected_currency)
        self.currency_combobox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        tk.Label(converter_frame, text="Ingresar valor en DOP", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=5)
        self.amount_entry = ttk.Entry(converter_frame, width=10)
        self.amount_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        convert_button = ttk.Button(converter_frame, text="Convertir", command=self.convert_currency)
        convert_button.grid(row=4, column=0, columnspan=2, pady=10)

    def create_stock_labels(self):
        for symbol in self.symbols:
            label = ttk.Label(self.root, text=f"{symbol}:", font=("Arial", 10, "bold"))
            result_label = ttk.Label(self.root, text="Cargando...", font=("Arial", 10))
            label.pack(pady=5)
            result_label.pack(pady=5)
            self.result_labels[symbol] = result_label

    def update_data(self):
        try:
            for symbol, result_label in self.result_labels.items():
                if self.selected_option.get() == "Bolsa":
                    self.update_stock_values(symbol, result_label)
                else:
                    # Obtiene datos de ticker en tiempo real para cada moneda o criptomoneda
                    ticker_data = self.exchange.fetch_ticker(symbol)

                    # Extrae la información necesaria y actualiza las etiquetas de resultados
                    price = ticker_data['ask']
                    result_label.config(text=f"Precio: {price}")

            # Actualiza las tasas de cambio si la opción actual es "Divisas"
            if self.selected_option.get() == "Divisas":
                self.update_currency_rates()

        except Exception as e:
            print(f"Error al obtener datos: {str(e)}")

        # Programa la próxima actualización
        self.root.after(self.update_interval, self.update_data)

    def update_stock_values(self, symbol, result_label):
        stock_data = self.get_stock_data(symbol)
        if stock_data:
            value = stock_data['latestPrice']
            market_cap = stock_data['marketCap']
            result_label.config(text=f"{symbol}: ${value} | Market Cap: ${market_cap}")
        else:
            result_label.config(text=f"{symbol}: No se pudo obtener el valor")

    def update_currency_rates(self):
        try:
            for currency, label_var in self.currency_labels.items():
                equivalent_in_dop = self.rates_updater.get_equivalent_in_dop(currency, 1)
                label_var.set(f"{equivalent_in_dop} DOP")
        except Exception as e:
            print(f"Error al actualizar tasas de cambio: {str(e)}")

    def convert_currency(self):
        try:
            amount = float(self.amount_entry.get())
            currency_code = self.selected_currency.get()
            equivalent_in_dop = self.rates_updater.get_equivalent_in_dop(currency_code, amount)
            messagebox.showinfo("Resultado de la conversión", f"{amount} {currency_code} equivale a {equivalent_in_dop} DOP")
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un valor numérico válido.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def get_stock_data(self, symbol):
        endpoint = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote"
        
        params = {
            "token": 'pk_7671b08c30654ab1a5ac1f186d116d14'
        }

        try:
            response = requests.get(endpoint, params=params)
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos para {symbol}: {e}")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanzasApp(root)
    root.mainloop()



