from pathlib import Path
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import ValidationError
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static, DataTable

from ozon_price_check.core_client import APIClient
from ozon_price_check.credentials import load_credentials
from ozon_price_check.onboarding import OnboardingScreen
from ozon_price_check.services.products import fetch_product_data, Section

BASE_DIR = Path(__file__).resolve().parent.parent


def parse_price(user_input: str) -> Decimal:
    """Parse price input accepting both comma and dot as decimal separator."""
    s = (user_input or "").strip()
    if not s:
        raise InvalidOperation("empty")
    if "," in s and "." in s:
        raise InvalidOperation("both separators")
    s = s.replace(",", ".")
    return Decimal(s)


class SectionTable(Static):
    """A single section with title and data table."""

    def __init__(self, section: Section, **kwargs) -> None:
        super().__init__(**kwargs)
        self.section = section
        self.table: DataTable | None = None

    def on_mount(self) -> None:
        title = Static(self.section["title"], classes="section-title")
        self.mount(title)

        table = DataTable(zebra_stripes=True)
        table.add_columns("Параметр", "Значение")

        for label, value in self.section["rows"]:
            table.add_row(label, value)

        self.table = table
        self.mount(table)


class ProductSections(ScrollableContainer):
    """Container for multiple product data sections."""

    def show_sections(self, sections: list[Section]) -> None:
        """Clear existing content and show new sections."""
        for child in list(self.children):
            child.remove()

        for section in sections:
            self.mount(SectionTable(section))

    def clear_sections(self) -> None:
        """Clear all sections."""
        for child in list(self.children):
            child.remove()


class MessagePanel(Static):
    """Panel for displaying errors/messages in the right column."""

    def show_error(self, text: str) -> None:
        self.remove_class("hidden")
        self.set_class(True, "error")
        self.update(text)

    def show_info(self, text: str) -> None:
        self.remove_class("hidden")
        self.set_class(False, "error")
        self.update(text)

    def hide(self) -> None:
        self.add_class("hidden")
        self.update("")


class AppTUI(App):
    """Micro TUI for quick SKU and price input and product information display."""

    CSS = """
    #main {
        layout: horizontal;
    }
    #left {
        width: 38%;
        min-width: 40;
        border: round $accent;
        padding: 1 2;
        height: 100%;
    }
    #right {
        width: 62%;
        border: round $accent;
        padding: 1 2;
        height: 100%;
    }
    .section-title {
        text-style: bold;
        background: $accent;
        color: $text;
        padding: 1;
        margin: 1 0;
    }
    Input {
        margin: 1 0;
    }
    #help {
        color: $text-muted;
        height: auto;
        padding-top: 1;
    }
    .hidden { display: none; }
    #msg.error { border: round $error; color: $error; }
    """

    BINDINGS = [
        Binding("f5", "query", "Запрос (F5)", show=True),
        Binding("escape", "clear_inputs", "Очистить ввод", show=False),
        Binding("ctrl+l", "clear_card", "Очистить карточку", show=False),
        Binding("f6", "swap_focus", "Фокус", show=False),
        Binding("ctrl+c", "quit", "Выход", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="main"):
            with Container(id="left"):
                yield Static("Ввод", classes="title")
                yield Input(placeholder="Артикул", id="sku")
                yield Input(placeholder="Цена (запятая или точка)", id="price")
                yield Static(
                    "Hotkeys: F5 — получить данные • Tab — смена поля • Esc — очистить ввод • Ctrl+L — очистить карточку",
                    id="help",
                )
            with Container(id="right"):
                yield Static("Информация о товаре", classes="title")
                yield MessagePanel(id="msg", classes="hidden")
                yield ProductSections(id="sections")
        yield Footer()

    async def on_mount(self) -> None:
        # Если учётки не сохранены — показ онбординга
        creds = load_credentials()
        if not (creds.api_key and creds.client_id):
            await self.push_screen(OnboardingScreen())
        self.query_one("#sku", Input).focus()

    def action_swap_focus(self) -> None:
        sku = self.query_one("#sku", Input)
        price = self.query_one("#price", Input)
        (price if sku.has_focus else sku).focus()

    def action_clear_inputs(self) -> None:
        sku = self.query_one("#sku", Input)
        price = self.query_one("#price", Input)
        sku.value, price.value = "", ""
        sku.focus()
        self.notify("Ввод очищен", timeout=1.2)

    def action_clear_card(self) -> None:
        self.query_one(ProductSections).clear_sections()
        self.notify("Карточка очищена", timeout=1.2)

    async def action_query(self) -> None:
        sku_inp = self.query_one("#sku", Input)
        price_inp = self.query_one("#price", Input)
        sections_view = self.query_one(ProductSections)
        msg = self.query_one("#msg", MessagePanel)

        sku = (sku_inp.value or "").strip()
        raw_price = (price_inp.value or "").strip()

        self.notify("Запрос: обрабатываю ввод…", timeout=1.2)

        if not sku:
            self.notify("Введите артикул", severity="warning", timeout=2.0)
            sku_inp.focus()
            return

        user_purchase_price: Decimal | None = None
        if raw_price:
            try:
                user_purchase_price = parse_price(raw_price)
            except InvalidOperation:
                msg.show_error(
                    "Ошибка: неверный формат цены. Используйте 123,45 или 123.45"
                )
                sections_view.add_class("hidden")
                sku_inp.focus()
                return

        # Берём секреты только из keychain/config
        creds = load_credentials()
        if not (creds.api_key and creds.client_id):
            msg.show_error(
                "Не заданы Client ID или API Key. Откройте онбординг и сохраните учётные данные."
            )
            sections_view.add_class("hidden")
            return

        try:
            async with APIClient(
                client_id=creds.client_id,
                api_key=creds.api_key,  # keyring already returns str
            ) as client:
                result: dict[str, Any] = await fetch_product_data(
                    sku, client=client, user_purchase_price=user_purchase_price
                )

            if "error" in result:
                msg.show_error(str(result["error"]))
                sections_view.add_class("hidden")
                sku_inp.focus()
                return

            msg.hide()
            sections_view.remove_class("hidden")
            sections_view.show_sections(result["sections"])
            self.notify("Готово: данные обновлены", timeout=1.2)

        except ValidationError as e:
            msg.show_error(f"Ошибка валидации данных:\n{e.json(indent=2)}")
            sections_view.add_class("hidden")
            sku_inp.focus()
            return
        except Exception as e:
            msg.show_error(f"Ошибка: {type(e).__name__}: {e}")
            sections_view.add_class("hidden")
            sku_inp.focus()
            return

        # Удобный цикл: фокус обратно на SKU + выделить всё
        sku_inp.focus()
        select_all = getattr(sku_inp, "action_select_all", None) or getattr(
            sku_inp, "select_all", None
        )
        if callable(select_all):
            select_all()


def main() -> None:
    """Entry point for the CLI application."""
    AppTUI().run()


if __name__ == "__main__":
    main()
