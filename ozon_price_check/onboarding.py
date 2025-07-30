from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Input, Button
from ozon_price_check.credentials import save_credentials


class OnboardingScreen(Screen):
    BINDINGS = [("f5", "save", "Сохранить (F5)")]

    def on_mount(self) -> None:
        self.query_one("#cid", Input).focus()

    def compose(self) -> ComposeResult:
        yield Static("Первый запуск — введите параметры OZON")
        yield Input(placeholder="Client ID (число)", id="cid")
        yield Input(placeholder="API Key", password=True, id="api")
        yield Input(placeholder="Base URL (опционально)", id="url")
        yield Button("Сохранить (F5)", id="save_btn")

    def action_save(self) -> None:
        cid = self.query_one("#cid", Input).value.strip()
        api = self.query_one("#api", Input).value.strip()
        url = self.query_one("#url", Input).value.strip() or None
        if not cid.isdigit() or not api:
            self.app.notify("Укажите Client ID (число) и API Key", severity="error")
            return
        save_credentials(client_id=int(cid), api_key=api, base_url=url)
        self.app.pop_screen()
        self.app.notify("Секреты сохранены", timeout=1.5)
