from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import CampaignCreateForm, CollateralForm, InClinicConfigurationForm
from .models import (
    Campaign,
    CampaignSystem,
    Collateral,
    FieldRepRecruitmentLink,
    InClinicConfiguration,
    SystemType,
    import_field_reps_from_csv,
)


class PublisherLoginView(LoginView):
    template_name = "core/login.html"


def publisher_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.groups.filter(name="Publisher").exists() and not request.user.is_superuser:
            raise PermissionDenied("Publisher role required")
        return view_func(request, *args, **kwargs)

    return _wrapped


@publisher_required
def publisher_dashboard(request):
    campaigns = Campaign.objects.filter(created_by=request.user).order_by("-created_at")
    return render(request, "core/publisher_dashboard.html", {"campaigns": campaigns})


@publisher_required
@require_http_methods(["GET", "POST"])
def campaign_add(request):
    if request.method == "POST":
        form = CampaignCreateForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.save()

            selected = form.cleaned_data["systems"]
            for system in selected:
                CampaignSystem.objects.create(campaign=campaign, system_type=system, is_enabled=True)

            FieldRepRecruitmentLink.objects.get_or_create(campaign=campaign)

            csv_file = request.FILES.get("field_rep_csv")
            csv_result = None
            if csv_file:
                csv_result = import_field_reps_from_csv(campaign, csv_file.read())
                for err in csv_result.errors:
                    messages.warning(request, err)
                if csv_result.created:
                    messages.success(request, f"Created {csv_result.created} field reps")

            request.session["campaign_create_result_id"] = campaign.id
            return redirect("campaign_create_result")
    else:
        form = CampaignCreateForm()

    return render(request, "core/campaign_add.html", {"form": form})


@publisher_required
def campaign_create_result(request):
    campaign_id = request.session.get("campaign_create_result_id")
    campaign = get_object_or_404(Campaign, id=campaign_id, created_by=request.user)
    return render(request, "core/campaign_create_result.html", {"campaign": campaign})


@publisher_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(created_by=request.user).order_by("-created_at")
    return render(request, "core/campaign_list.html", {"campaigns": campaigns})


@publisher_required
def inclinic_landing(request, campaign_uuid):
    campaign = get_object_or_404(Campaign, campaign_uuid=campaign_uuid, created_by=request.user)
    campaign_system = get_object_or_404(CampaignSystem, campaign=campaign, system_type=SystemType.INCLINIC)
    return render(request, "core/inclinic_landing.html", {"campaign": campaign, "campaign_system": campaign_system})


@publisher_required
@require_http_methods(["GET", "POST"])
def inclinic_configure(request, campaign_uuid):
    campaign = get_object_or_404(Campaign, campaign_uuid=campaign_uuid, created_by=request.user)
    campaign_system = get_object_or_404(CampaignSystem, campaign=campaign, system_type=SystemType.INCLINIC)
    config = InClinicConfiguration.objects.filter(campaign_system=campaign_system).first()

    if request.method == "POST":
        form = InClinicConfigurationForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.campaign_system = campaign_system
            saved.save()
            messages.success(request, "In-Clinic configuration saved")
            return redirect("campaign_details", campaign_uuid=campaign_uuid)
    else:
        form = InClinicConfigurationForm(instance=config)

    return render(request, "core/inclinic_configure.html", {"campaign": campaign, "form": form})


@publisher_required
def campaign_details(request, campaign_uuid):
    campaign = get_object_or_404(Campaign, campaign_uuid=campaign_uuid, created_by=request.user)
    campaign_system = CampaignSystem.objects.filter(campaign=campaign, system_type=SystemType.INCLINIC).first()
    config = InClinicConfiguration.objects.filter(campaign_system=campaign_system).first() if campaign_system else None
    return render(request, "core/campaign_details.html", {"campaign": campaign, "config": config, "campaign_system": campaign_system})


@publisher_required
def collateral_dashboard(request):
    search_uuid = request.GET.get("campaign_uuid", "").strip()
    campaign = None
    collaterals = Collateral.objects.none()
    if search_uuid:
        campaign = Campaign.objects.filter(campaign_uuid=search_uuid, created_by=request.user).first()
        if campaign:
            collaterals = Collateral.objects.filter(campaign_system__campaign=campaign, campaign_system__system_type=SystemType.INCLINIC).order_by("sort_order", "-created_at")
    return render(request, "core/collateral_dashboard.html", {"search_uuid": search_uuid, "campaign": campaign, "collaterals": collaterals})


@publisher_required
@require_http_methods(["GET", "POST"])
def collateral_add(request, campaign_uuid):
    campaign = get_object_or_404(Campaign, campaign_uuid=campaign_uuid, created_by=request.user)
    campaign_system = get_object_or_404(CampaignSystem, campaign=campaign, system_type=SystemType.INCLINIC)

    if request.method == "POST":
        form = CollateralForm(request.POST, request.FILES)
        if form.is_valid():
            collateral = form.save(commit=False)
            collateral.campaign_system = campaign_system
            collateral.save()
            messages.success(request, "Collateral added")
            return redirect("collateral_dashboard")
    else:
        form = CollateralForm()
    return render(request, "core/collateral_form.html", {"form": form, "campaign": campaign})


@publisher_required
@require_http_methods(["GET", "POST"])
def collateral_edit(request, collateral_id):
    collateral = get_object_or_404(Collateral, id=collateral_id, campaign_system__campaign__created_by=request.user)
    if request.method == "POST":
        form = CollateralForm(request.POST, request.FILES, instance=collateral)
        if form.is_valid():
            form.save()
            messages.success(request, "Collateral updated")
            return redirect("collateral_dashboard")
    else:
        form = CollateralForm(instance=collateral)
    return render(request, "core/collateral_form.html", {"form": form, "campaign": collateral.campaign_system.campaign, "collateral": collateral})


@publisher_required
@require_http_methods(["POST"])
def collateral_delete(request, collateral_id):
    collateral = get_object_or_404(Collateral, id=collateral_id, campaign_system__campaign__created_by=request.user)
    collateral.delete()
    messages.success(request, "Collateral deleted")
    return redirect("collateral_dashboard")


@login_required
def collateral_preview(request, collateral_id):
    collateral = get_object_or_404(Collateral, id=collateral_id)
    return render(request, "core/collateral_preview.html", {"collateral": collateral})


def forbidden_view(request, exception=None):
    return HttpResponseForbidden("Forbidden")
