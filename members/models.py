from django.db import models
from django.utils import timezone


class Member(models.Model):
    """A member of Zion Baptist Church."""

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('divorced', 'Divorced'),
    ]

    ORGAN_CHOICES = [
        ('men', "Men's Fellowship"),
        ('women', "Women's Fellowship"),
        ('youth', 'Youth Fellowship'),
    ]

    # Auto-generated unique ID
    member_id = models.CharField(
        max_length=20,
        unique=True,          # <-- ADD this
        blank=True,
        help_text="Auto-generated on save (e.g., ZBC-2026-0001)"
    )

    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(
        max_length=10,
        choices=MARITAL_STATUS_CHOICES,
        blank=True
    )

    # Contact info
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    occupation = models.CharField(max_length=150, blank=True)

    # Church info
    organ = models.CharField(
        max_length=10,
        choices=ORGAN_CHOICES,
        blank=True,
        help_text="The fellowship group this member belongs to"
    )
    joined_date = models.DateField(null=True, blank=True)
    is_baptized = models.BooleanField(default=False)

    # Photo
    photo = models.ImageField(
        upload_to='member_photos/',
        blank=True,
        null=True,
        help_text="Passport-size or 4x4 photo"
    )

    # Pastoral info
    prayer_needs = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Soft delete
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to mark as inactive (soft delete)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate member_id if not already set
        if not self.member_id:
            year = timezone.now().year
            # Get the last member_id for this year
            last_member = Member.objects.filter(
                member_id__startswith=f'ZBC-{year}-'
            ).order_by('-member_id').first()

            if last_member and last_member.member_id:
                # Extract the last number and increment
                last_number = int(last_member.member_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.member_id = f'ZBC-{year}-{new_number:04d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def age(self):
        """Calculate current age from date of birth."""
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Member"
        verbose_name_plural = "Members"


class Family(models.Model):
    """Family information for a married member."""

    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name='family',
        help_text="The member this family belongs to"
    )
    spouse_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Full name of spouse"
    )
    wedding_anniversary = models.DateField(
        null=True,
        blank=True,
        help_text="Optional — date of wedding"
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.member} — Family"

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"


class Child(models.Model):
    """A child of a member (max 7 recommended per family)."""

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='children'
    )
    name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=Member.GENDER_CHOICES,
        blank=True
    )
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    class Meta:
        ordering = ['date_of_birth']
        verbose_name = "Child"
        verbose_name_plural = "Children"


class PrayerRequest(models.Model):
    """A prayer request submitted by or for a member."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('answered', 'Answered'),
        ('closed', 'Closed'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='prayer_requests',
        help_text="The member this prayer request is for"
    )
    request = models.TextField(help_text="The prayer request details")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    date_submitted = models.DateField(auto_now_add=True)
    date_answered = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.member} — {self.request[:50]}"

    class Meta:
        ordering = ['-date_submitted']
        verbose_name = "Prayer Request"
        verbose_name_plural = "Prayer Requests"


class Talent(models.Model):
    """A skill, gift, or interest that a member has for ministry service."""

    CATEGORY_CHOICES = [
        ('music', 'Music & Worship'),
        ('teaching', 'Teaching & Preaching'),
        ('ushering', 'Ushering & Hospitality'),
        ('media', 'Media & Technology'),
        ('children', 'Children & Youth'),
        ('administration', 'Administration & Finance'),
        ('outreach', 'Evangelism & Outreach'),
        ('prayer', 'Prayer & Intercession'),
        ('helps', 'Helps & Practical Service'),
        ('other', 'Other'),
    ]

    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='talents',
        help_text="The member with this talent"
    )
    name = models.CharField(
        max_length=150,
        help_text="e.g., Singing, Piano, Teaching Children, Ushering"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    skill_level = models.CharField(
        max_length=15,
        choices=SKILL_LEVEL_CHOICES,
        default='intermediate'
    )
    is_available_for_ministry = models.BooleanField(
        default=True,
        help_text="Is this member willing to serve in this area?"
    )
    notes = models.TextField(blank=True)
    recorded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} — {self.name}"

    class Meta:
        ordering = ['member__last_name', 'name']
        verbose_name = "Talent"
        verbose_name_plural = "Talents"