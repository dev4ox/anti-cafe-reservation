import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from booking.models import Reservation, Table
from catalog.models import BoardGame, Product
from inbox.models import ContactMessage
from site_settings.models import SiteSettings, SpecialDay, WeeklySchedule


class Command(BaseCommand):
    """Очищает все данные приложения (без удаления пользователей)."""
    help = "Delete all app data (reservations, tables, catalog, messages, settings, schedules)."

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки."""
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirm deleting all app data.",
        )
        parser.add_argument(
            "--with-media",
            action="store_true",
            help="Also remove uploaded media files.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Удаляет данные приложений."""
        if not options["yes"]:
            self.stdout.write(self.style.ERROR("Refusing to run without --yes."))
            return

        Reservation.objects.all().delete()
        Table.objects.all().delete()
        BoardGame.objects.all().delete()
        Product.objects.all().delete()
        ContactMessage.objects.all().delete()
        WeeklySchedule.objects.all().delete()
        SpecialDay.objects.all().delete()
        SiteSettings.objects.all().delete()

        if options.get("with_media"):
            self._clear_media_root()

        self.stdout.write(self.style.SUCCESS("All app data deleted."))

    def _clear_media_root(self) -> None:
        """Удаляет все файлы внутри MEDIA_ROOT, не трогая саму папку."""
        media_root = Path(getattr(settings, "MEDIA_ROOT", ""))
        if not media_root:
            return
        if not media_root.exists() or not media_root.is_dir():
            return
        for entry in media_root.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry, ignore_errors=True)
            else:
                try:
                    entry.unlink(missing_ok=True)
                except TypeError:
                    if entry.exists():
                        entry.unlink()
