from django.db import models


class Contact(models.Model):
    TYPE_CHOICES = [
        ('general', 'Umumiy'),
        ('admission', 'Qabul'),
        ('complaint', 'Shikoyat'),
        ('suggestion', 'Taklif'),
        ('other', 'Boshqa'),
    ]
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('read', "O'qilgan"),
        ('replied', 'Javob berilgan'),
        ('closed', 'Yopilgan'),
    ]

    full_name = models.CharField(max_length=200, verbose_name="F.I.Sh")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, verbose_name="Elektron pochta")
    contact_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general', verbose_name="Murojaat turi")
    subject = models.CharField(max_length=300, verbose_name="Mavzu")
    message = models.TextField(verbose_name="Xabar matni")
    privacy_agreed = models.BooleanField(default=False, verbose_name="Maxfiylik siyosatiga rozilik")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Holati")
    admin_reply = models.TextField(blank=True, verbose_name="Administrator javobi")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP manzili")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqti")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Javob berilgan vaqti")

    class Meta:
        verbose_name = 'Murojaat'
        verbose_name_plural = 'Murojaatlar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject} ({self.get_contact_type_display()})"
