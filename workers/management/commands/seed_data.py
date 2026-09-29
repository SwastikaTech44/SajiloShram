from django.core.management.base import BaseCommand
from workers.models import District, Municipality, Skill

DATA = {
    'Kaski': [
        'Pokhara Metropolitan City', 'Annapurna Rural Municipality',
        'Machhapuchchhre Rural Municipality', 'Madi Rural Municipality',
        'Rupa Rural Municipality',
    ],
    'Syangja': [
        'Galyang Municipality', 'Chapakot Municipality', 'Putalibazar Municipality',
        'Bhirkot Municipality', 'Waling Municipality', 'Arjun Chaupari Rural Municipality',
        'Aandhikhola Rural Municipality', 'Kaligandaki Rural Municipality',
        'Phedikhola Rural Municipality', 'Harinas Rural Municipality',
        'Biruwa Rural Municipality',
    ],
    'Baglung': [
        'Baglung Municipality', 'Dhorpatan Municipality', 'Galkot Municipality',
        'Jaimuni Municipality', 'Bareng Rural Municipality', 'Khathekhola Rural Municipality',
        'Taman Khola Rural Municipality', 'Tara Khola Rural Municipality',
        'Nisikhola Rural Municipality', 'Badigad Rural Municipality',
    ],
    'Parbat': [
        'Kushma Municipality', 'Phalebas Municipality', 'Jaljala Rural Municipality',
        'Paiyun Rural Municipality', 'Mahashila Rural Municipality',
        'Modi Rural Municipality', 'Bihadi Rural Municipality',
    ],
    'Lalitpur': [
        'Lalitpur Metropolitan City', 'Godawari Municipality', 'Mahalaxmi Municipality',
        'Konjyosom Rural Municipality', 'Bagmati Rural Municipality',
        'Mahankal Rural Municipality',
    ],
    'Bhaktapur': [
        'Bhaktapur Municipality', 'Changunarayan Municipality',
        'Madhyapur Thimi Municipality', 'Suryabinayak Municipality',
    ],
    'Chitwan': [
        'Bharatpur Metropolitan City', 'Kalika Municipality', 'Khairahani Municipality',
        'Madi Municipality', 'Ratnanagar Municipality', 'Rapti Municipality',
        'Ichchhakamana Rural Municipality',
    ],
}

SKILLS = [
    'Mason', 'Painter', 'Carpenter', 'Plumber', 'Electrician',
    'Farm Laborer', 'Harvester', 'Driver', 'Construction Helper',
]


class Command(BaseCommand):
    help = 'Load starter districts, municipalities and skills'

    def handle(self, *args, **options):
        for district_name, municipalities in DATA.items():
            district, _ = District.objects.get_or_create(name=district_name)
            for m in municipalities:
                Municipality.objects.get_or_create(district=district, name=m)
        for s in SKILLS:
            Skill.objects.get_or_create(name=s)
        self.stdout.write(self.style.SUCCESS('Seed data loaded'))