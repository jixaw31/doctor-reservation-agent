from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import jdatetime


pay_load = {
        "id": 2,
        "name": "دکتر مایکل چن",
        "profession": "متخصص مغز و اعصاب",
        "title": "رئیس بخش مغز و اعصاب",
        "description": "متخصص در اختلالات نورودژنراتیو و توانبخشی سکته مغزی. تحقیقات پیشگام در زمینه بیماری آلزایمر و درمان پارکینسون.",
        "specialties": ["اختلالات نورودژنراتیو", "توانبخشی سکته مغزی", "اختلالات حرکتی"],
        "experience_years": 20,
        "education": "دکترای تخصصی و فوق دکترای علوم اعصاب - دانشگاه جانز هاپکینز",
        "hospital": "مرکز علوم اعصاب پاسیفیک",
        "location": "مشهد، بلوار وکیل‌آباد",
        "rating": 408,
        "reviews_count": 287,
        "availability": ["یکشنبه", "سه‌شنبه", "پنجشنبه"],
        "consultation_fee": 300,
        "phone": "۰۵۱-۵۵۵۵-۰۴۵۶",
        "email": "dr.michael.chen@pacificneuro.com",
        "is_accepting_patients": True,
        "languages": ["فارسی", "انگلیسی", "ماندارین"],
        "profile_image": "michael_chen.jpg"
    }


PERSIAN_WEEKDAYS = {
        0: "دوشنبه",
        1: "سه‌شنبه",
        2: "چهارشنبه",
        3: "پنجشنبه",
        4: "جمعه",
        5: "شنبه",
        6: "یکشنبه",
    }

def find_next_available_appointment(doctor):
    """Find the next available day for the doctor."""

    if not doctor["is_accepting_patients"]:
        return None

    now = datetime.now(ZoneInfo("Asia/Tehran"))

    # Check today + the next 6 days
    for days_ahead in range(7):
        candidate = now + timedelta(days=days_ahead)

        weekday = PERSIAN_WEEKDAYS[candidate.weekday()]

        if weekday in doctor["availability"]:
            # Example/default appointment time.
            # Replace this with actual slot lookup later.
            appointment_time = candidate.replace(
                hour=10,
                minute=0,
                second=0,
                microsecond=0,
            )

            # Don't return a time that has already passed today.
            if appointment_time <= now:
                continue

            return appointment_time

    return None


def format_appointment_confirmation(doctor, appointment_time, patient_name):
    """Create a patient-facing appointment confirmation."""

    jalali = jdatetime.datetime.fromgregorian(
        datetime=appointment_time
    )

    weekday = PERSIAN_WEEKDAYS[appointment_time.weekday()]

    return f"""
✅ نوبت شما با موفقیت ثبت شد

👨‍⚕️ پزشک: {doctor["name"]}
🧠 تخصص: {doctor["profession"]}

📅 تاریخ: {weekday} {jalali.day} {jalali.strftime("%B")} {jalali.year}
🕐 ساعت: {appointment_time.strftime("%H:%M")}

📍 محل:
{doctor["hospital"]}
{doctor["location"]}

👤 بیمار: {patient_name}

💳 هزینه ویزیت: {doctor["consultation_fee"]:,} تومان

📞 تلفن مرکز: {doctor["phone"]}

🔖 کد پیگیری: AP-{doctor["id"]}-{jalali.strftime("%y%m%d%H%M")}

وضعیت نوبت: تأیید شده ✅

لطفاً ۱۰ تا ۱۵ دقیقه پیش از زمان نوبت در مرکز حضور داشته باشید.
"""


# --------------------------------------------------
# Example
# --------------------------------------------------

patient_name = "محمد علی"

appointment = find_next_available_appointment(pay_load)



if __name__ == "__main__":
    if appointment is None:
        print("هیچ نوبت نزدیکی برای این پزشک پیدا نشد.")
    else:
        confirmation = format_appointment_confirmation(
            doctor=pay_load,
            appointment_time=appointment,
            patient_name=patient_name,
        )

        print(confirmation)