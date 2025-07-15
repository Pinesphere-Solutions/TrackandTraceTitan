from django.core.management.base import BaseCommand
from modelmasterapp.models import TrayId

class Command(BaseCommand):
    help = 'Load NB and JB trays into DB'

    def handle(self, *args, **kwargs):
        nb_trays = [
            TrayId(tray_id=f"NB-A{str(i).zfill(5)}", tray_type="Normal", tray_capacity=16)
            for i in range(1, 101)
        ]
        jb_trays = [
            TrayId(tray_id=f"JB-A{str(i).zfill(5)}", tray_type="Jumbo", tray_capacity=12)
            for i in range(1, 101)
        ]
        TrayId.objects.bulk_create(nb_trays + jb_trays)
        self.stdout.write(self.style.SUCCESS('Successfully loaded all trays'))
