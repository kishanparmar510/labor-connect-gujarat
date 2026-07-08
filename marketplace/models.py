from django.db import models
from django.contrib.auth.models import User

SKILL_CHOICES = [
    ('mason', 'Mason (Kadiya)'),
    ('carpenter', 'Carpenter (Suthar)'),
    ('plumber', 'Plumber'),
    ('electrician', 'Electrician'),
    ('painter', 'Painter'),
    ('welder', 'Welder'),
    ('laborer', 'Helper / General Labor'),
]


# marketplace/models.py me sabse upar ya jahan LOCATION_CHOICES likha hai, wahan ye paste kar do:

LOCATION_CHOICES = [
    # ---- AHMEDABAD ----
    ('bopal_ahmedabad', 'Bopal (Ahmedabad)'),
    ('satellite_ahmedabad', 'Satellite (Ahmedabad)'),
    ('vastrapur_ahmedabad', 'Vastrapur (Ahmedabad)'),
    ('naroda_ahmedabad', 'Naroda (Ahmedabad)'),

    # ---- RAJKOT ----
    ('gondal_chowkdi_rajkot', 'Gondal Chowkdi (Rajkot)'),
    ('bus_stand_rajkot', 'Bus Stand (Rajkot)'),
    ('indira_circle_rajkot', 'Indira Circle (Rajkot)'),
    ('kalawad_road_rajkot', 'Kalawad Road (Rajkot)'),

    # ---- PORBANDAR ----
    ('chhaya_porbandar', 'Chhaya (Porbandar)'),
    ('sudama_puri_porbandar', 'Sudama Puri (Porbandar)'),
    ('khapat_porbandar', 'Khapat (Porbandar)'),
    ('kamla_bagh_porbandar', 'Kamla Bagh (Porbandar)'),

    # ---- BHAVNAGAR ----
    ('kaliyabid_bhavnagar', 'Kaliyabid (Bhavnagar)'),
    ('ghogha_circle_bhavnagar', 'Ghogha Circle (Bhavnagar)'),
    ('chitra_bhavnagar', 'Chitra (Bhavnagar)'),
    ('subhashnagar_bhavnagar', 'Subhashnagar (Bhavnagar)'),
]

AVAILABILITY_CHOICES = [
    ('available', 'Available Today'),
    ('busy', 'Busy'),
    ('soon', 'Available Soon'),
]

class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15, unique=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    skill = models.CharField(max_length=30, choices=SKILL_CHOICES)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Daily rate in INR (optional)")
    bio = models.TextField(blank=True, max_length=500)
    profile_picture = models.ImageField(upload_to='workers/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.get_skill_display()}"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0.0

    @property
    def review_count(self):
        return self.reviews.count()

class Review(models.Model):
    worker = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.worker.name} by {self.customer_name} ({self.rating}★)"
