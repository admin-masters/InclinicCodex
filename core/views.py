from datetime import timedelta
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from .forms import CampaignForm, FieldRepForm
from .models import ActivityEvent, Campaign, CampaignCycle, Doctor, FieldRepresentative, ShareRecord
from .services import get_active_collaterals, get_current_cycle


def dashboard(request):
    return render(request, "core/dashboard.html", {"campaigns": Campaign.objects.all().order_by("-id")})


def campaign_create(request):
    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save()
            return redirect("campaign_edit", campaign_id=campaign.id)
    else:
        form = CampaignForm()
    return render(request, "core/campaign_form.html", {"form": form})


def campaign_edit(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    if request.method == "POST":
        if "create_cycle" in request.POST:
            CampaignCycle.objects.create(
                campaign=campaign,
                cycle_number=int(request.POST["cycle_number"]),
                start_date=request.POST["start_date"],
                end_date=request.POST["end_date"],
                title=request.POST["title"],
                message_template=request.POST["message_template"],
                reminder_template=request.POST["reminder_template"],
                pdf_url=request.POST["pdf_url"],
                video_vimeo_url=request.POST["video_vimeo_url"],
            )
        elif "add_rep" in request.POST:
            FieldRepresentative.objects.create(
                campaign=campaign,
                name=request.POST["name"],
                email=request.POST["email"],
                whatsapp_number=request.POST["whatsapp_number"],
                is_active=True,
            )
        return redirect("campaign_edit", campaign_id=campaign.id)
    return render(request, "core/campaign_edit.html", {"campaign": campaign, "reps": campaign.field_reps.all(), "cycles": campaign.cycles.all()})


def field_rep_list(request):
    reps = FieldRepresentative.objects.order_by("campaign_id", "name")
    if request.method == "POST":
        rep = get_object_or_404(FieldRepresentative, pk=request.POST["rep_id"])
        rep.is_active = request.POST.get("action") == "activate"
        rep.save(update_fields=["is_active"])
        return redirect("field_rep_list")
    return render(request, "core/field_reps.html", {"reps": reps, "form": FieldRepForm()})


def share_collateral(request):
    campaigns = Campaign.objects.all()
    if request.method == "POST":
        rep = get_object_or_404(FieldRepresentative, pk=request.POST["field_rep_id"], is_active=True)
        campaign = rep.campaign
        cycle = get_object_or_404(CampaignCycle, pk=request.POST["cycle_id"], campaign=campaign)
        doctor, _ = Doctor.objects.get_or_create(whatsapp_number=request.POST["doctor_whatsapp"])
        share = ShareRecord.objects.create(
            campaign=campaign,
            cycle=cycle,
            field_rep=rep,
            doctor=doctor,
            whatsapp_message=cycle.message_template,
            is_reminder=request.POST.get("is_reminder") == "1",
        )
        url = f"https://wa.me/{doctor.whatsapp_number}?text={share.whatsapp_message} {request.build_absolute_uri(reverse('doctor_verify', args=[share.token]))}"
        return render(request, "core/share_success.html", {"share": share, "url": url})
    return render(request, "core/share_form.html", {"campaigns": campaigns})


def doctor_status_list(request):
    rep_id = request.GET.get("rep_id")
    if not rep_id:
        return render(request, "core/doctor_status.html", {"shares": []})
    shares = ShareRecord.objects.filter(field_rep_id=rep_id).order_by("-shared_at")
    return render(request, "core/doctor_status.html", {"shares": shares})


def doctor_verify(request, token):
    share = get_object_or_404(ShareRecord, token=token)
    ActivityEvent.objects.create(share=share, doctor=share.doctor, event_type="whatsapp_click")
    if request.method == "POST":
        if request.POST["whatsapp_number"] != share.doctor.whatsapp_number:
            return HttpResponseBadRequest("Number mismatch")
        share.doctor.verified_at = timezone.now()
        share.doctor.save(update_fields=["verified_at"])
        return redirect("doctor_landing", token=token)
    return render(request, "core/doctor_verify.html", {"share": share})


def doctor_landing(request, token):
    share = get_object_or_404(ShareRecord, token=token)
    ActivityEvent.objects.create(share=share, doctor=share.doctor, event_type="landing_visit")
    if share.status != ShareRecord.STATUS_READ:
        share.status = ShareRecord.STATUS_READ
        share.read_at = timezone.now()
        share.save(update_fields=["status", "read_at"])
    return render(request, "core/doctor_landing.html", {"share": share})


def track_activity(request, share_id, event_type):
    share = get_object_or_404(ShareRecord, pk=share_id)
    value = float(request.POST.get("value", "1"))
    ActivityEvent.objects.create(share=share, doctor=share.doctor, event_type=event_type, value=value)
    return JsonResponse({"ok": True})
