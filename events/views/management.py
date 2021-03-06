from ..models import Event, Inscription, ExternInscription, Invitation
from bde.shortcuts import is_contributor
from shop.models import BuyingHistory

from django.contrib.auth.models import User
from django.db.models import Count
from django.core.mail import send_mail
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.templatetags.static import static

import json


@permission_required('events.manage_entries')
def admin_management(request, eid):
    event = get_object_or_404(Event, id=eid)
    if event.gestion is None:
        raise Http404

    context = {'event': event}

    return render(request, 'events/admin/management_index.html', context)


@permission_required('events.manage_entries')
def management_list_users(request, eid):
    e = get_object_or_404(Event, id=eid)
    ret = {}
    if request.method == "OPTIONS":
        # Reg
        if e.gestion == Event.GESTION_NOLIMIT:
            already_in_list = []
            ret['reg'] = []
            for ins in Inscription.objects.filter(event=e).select_related("user__profile").select_related('event').select_related("user__contribution").annotate(null_nick=Count('user__profile__nickname')).order_by('null_nick', '-user__profile__nickname', '-user__last_name', '-user__first_name', '-user__username').reverse():
                ret['reg'].append({
                    "display_name": str(ins.user.profile),
                    "picture": ins.user.profile.get_picture_url(),
                    "color": "bg-blue" if ins.in_date is not None else "bg-green" if is_contributor(ins.user) else "bg-red",
                    "type": "reg",
                    "id": ins.id,
                    "user": False,
                })
                already_in_list.append(str(ins.user.profile))
            for user in User.objects.all().select_related('profile'):
                if str(user.profile) not in already_in_list:
                    ret['reg'].append({
                        "display_name": str(user.profile),
                        "picture": user.profile.get_picture_url(),
                        "color": "bg-green" if is_contributor(user) else "bg-red",
                        "type": "reg",
                        "id": user.id,
                        "user": True,
                        'username': user.username,
                    })
        else:
            ret['reg'] = [{
                "display_name": str(ins.user.profile),
                'username': ins.user.username,
                "picture": ins.user.profile.get_picture_url(),
                "color": "bg-blue" if ins.in_date is not None else "bg-green" if is_contributor(ins.user) else "bg-red",
                "type": "reg",
                "id": ins.id,
                "formula": ins.formula.name if ins.formula else None,
                "formula_price": (ins.formula.price_contributor if is_contributor(ins.user) else ins.formula.price_non_contributor) if ins.formula else None,
            } for ins in Inscription.objects.filter(event=e).select_related("user__profile").select_related('event').select_related("user__contribution").annotate(null_nick=Count('user__profile__nickname')).order_by('null_nick', '-user__profile__nickname', '-user__last_name', '-user__first_name', '-user__username').reverse()]

        ret['ext_reg'] = [{
            "display_name": "{} {} ({})".format(ins.last_name, ins.first_name, ins.via.name),
            "picture": static('images/default_user_icon.png'),
            "color": "bg-blue" if ins.in_date is not None else "",
            "type": "ext_reg",
            "id": ins.id,
            "formula": ins.formula.name if ins.formula else None,
            "formula_price": ins.formula.price_non_contributor if ins.formula else None,
        } for ins in ExternInscription.objects.filter(event=e).select_related('event').select_related('via').order_by('last_name', 'first_name')]
        ret['invits'] = [{
            "display_name": "{} {} (invité par {})".format(ins.first_name, ins.last_name, str(ins.user.profile)),
            "picture": static('images/default_user_icon.png'),
            "color": "bg-blue" if ins.in_date is not None else "",
            "type": "invit",
            "id": ins.id,
            "formula": ins.formula.name if ins.formula else None,
            "formula_price": ins.formula.price_non_contributor if ins.formula else None,
        } for ins in Invitation.objects.filter(event=e).select_related('event').select_related('user__profile').order_by('last_name', 'first_name')]
        return JsonResponse(ret)


@permission_required('events.manage_entries')
def management_info_user(request, eid, type, iid):
    e = get_object_or_404(Event, id=eid)
    context = {'type': type, 'iid': iid, 'event': e}
    if type == "reg":
        ins = Inscription.objects.select_related('user__profile').get(event=e, id=iid)
        context['ins'] = ins
        context['display_name'] = str(ins.user.profile)
        context['products'] = [prod for prod in BuyingHistory.get_all_bought_products(ins.user) if prod.event == e]
    elif type == "ext_reg":
        pass
    else:
        pass
    return render(request, "events/admin/info_popup.html", context)


@permission_required('events.manage_entries')
def management_ack(request, eid, type, iid):
    e = get_object_or_404(Event, id=eid)
    req = json.loads(request.read().decode())
    if type == "reg":
        if req.get('user'):
            u = User.objects.get(id=iid)
            ins = Inscription.objects.create(event=e, user=u)
        else:
            ins = Inscription.objects.get(event=e, id=iid)
        ins.in_date = timezone.now()
        ins.save()
        return JsonResponse({"status": 1, "ins_id": ins.id})
    elif type == "ext_reg":
        pass
    else:
        pass
    return render(request, "events/admin/info_popup.html")


@permission_required('events.manage_entries')
def management_nl_ack(request):
    req = json.loads(request.read().decode())
    e = get_object_or_404(Event, id=req['eid'])

    if req['type'] == "reg":
        if req.get('user'):
            u = User.objects.get(id=req['iid'])
            ins = Inscription.objects.create(event=e, user=u)
        else:
            ins = Inscription.objects.get(event=e, id=req['iid'])
    elif req['type'] == "ext_reg":
        ins = ExternInscription.objects.get(event=e, id=req['iid'])
        send_mail_photos_nl(e, ins)
    else:
        ins = Invitation.objects.get(event=e, id=req['iid'])
        send_mail_photos_nl(e, ins)

    ins.payment_mean = req.get("payment_mean")
    ins.in_date = timezone.now()
    ins.save()
    r = JsonResponse({"status": 1, 'ins_id': ins.id})
    return r


@permission_required('events.manage_entries')
def management_nl_del(request, eid, type, iid):
    e = get_object_or_404(Event, id=eid)
    klass = ""
    if type == "reg":
        ins = Inscription.objects.get(event=e, id=iid)
        if(is_contributor(ins.user)):
            klass = "bg-green"
        else:
            klass = "bg-red"
    elif type == "ext_reg":
        ins = ExternInscription.objects.get(event=e, id=iid)
    else:
        ins = Invitation.objects.get(event=e, id=iid)

    ins.payment_mean = None
    ins.in_date = None
    ins.save()
    return JsonResponse({"status": 1, "klass": klass})


@permission_required('events.manage_entries')
def management_nl_info_user(request, eid, type, iid):
    e = get_object_or_404(Event, id=eid)
    context = {'type': type, 'iid': iid, 'eid': eid, 'event': e}
    if type == "reg":
        ins = Inscription.objects.select_related('user__profile').get(event=e, id=iid)
        context['display_name'] = str(ins.user.profile)
    elif type == "ext_reg":
        ins = ExternInscription.objects.get(event=e, id=iid)
        context['display_name'] = "{} {}".format(ins.first_name, ins.last_name)
    else:
        ins = Invitation.objects.get(event=e, id=iid)
        context['display_name'] = "{} {}".format(ins.first_name, ins.last_name)
    context['ins'] = ins
    return render(request, "events/admin/info_nl_popup.html", context)


@permission_required('events.manage_entries')
def management_nl_ack_popup(request, iid, eid):
    context = {"eid": eid, "iid": iid}
    return render(request, "events/admin/nl_ack_popup.html", context)


def send_mail_photos_nl(event, inv):
    if event.photo_path:
        send_mail('Photos ' + event.name, '''
Bonjour {first_name},
Tu viens de rentrer dans la super soirée {event_name} :)

On espère que tu vas bien t'amuser, et profiter, mais n'oublies pas: l'abus d'alcool est dangereux pour la santé :p


Sache que tu pourras trouver les photos de l'événement sur le lien suivant dès samedi prochain {link}

Nous te souhaitons une bonne semaine et espérons te revoir bientôt :)

L'équipe du BDE
'''.format(first_name=inv.first_name, event_name=event.name, link="https://enib.net/photo/browse/" + event.photo_path), 'noreply@enib.net', [inv.mail, ])

