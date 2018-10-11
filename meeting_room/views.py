import json
from channels import Channel
from django.shortcuts import render, get_object_or_404, render_to_response, RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from .models import Meeting
from webrtc_meetings.routing import store as attendance_register
from webrtc_meetings.routing import ONLINE
from model_base.attendant import Attendant
from utils.helpers import get_client_ip
from utils.logger import glogger
from utils.helpers import login_required

# Create your views here.
def join_meeting(request, room_id):
    try:
        meeting = Meeting.get_meeting(room_id)
    except Meeting.DoesNotExist:
        return HttpResponseNotFound()
    return render_to_response('meeting_room/meeting.html', {'ice_uri': reverse('get_ice', kwargs={'room_id': room_id}),
                                                            'meeting': meeting},
                              context_instance=RequestContext(request))


def get_ice(request, room_id):
    try:
        meeting = Meeting.get_meeting(room_id)
    except Meeting.DoesNotExist:
        return HttpResponseNotFound()
    return HttpResponse(json.dumps(settings.ICE_SERVERS), content_type='application/json')


def clear_attendants(request):
    attendants = []
    attendant_datas = attendance_register.hvals(ONLINE)
    map(lambda data: attendants.append(Attendant.loads(data)), attendant_datas)
    for attendant in attendants:
	attendance_register.hdel(ONLINE, attendant['id'])
    #attendant_datas = attendance_register.hvals(ONLINE)
    return HttpResponse(json.dumps(attendants), content_type='application/json')


def online_attendants(request):
    attendants = []
    attendant_datas = attendance_register.hvals(ONLINE)
    map(lambda data: attendants.append(Attendant.loads(data)), attendant_datas)
    #glogger.debug(json.dumps(attendants))
    return HttpResponse(json.dumps(attendants), content_type='application/json')


@login_required
def create_room(request, user):
    try:
        request_data = request.POST if request.method == 'POST' else request.GET
        #duration = int(request_data['duration'])
        duration = int(request_data.get('duration',45))
        timezone_requested = request_data.get('timezone', settings.TIME_ZONE)
        description = request_data.get('description', '')
        meeting = Meeting.objects.create(creator=user, timezone=timezone_requested, activation_date=timezone.now(),
                                         duration=duration, description=description)
        meeting_url = meeting.meeting_url()     # to generate the meeting url
        return HttpResponse(json.dumps({'creator': user.username, 'start_date': meeting.activation_date,
                                        'duration': meeting.duration, 'meeting_url': meeting_url,
                                        'description': meeting.description},
                                       cls=DjangoJSONEncoder),)
    except Exception, ex:
        raise ex
    return HttpResponseNotFound()   # generally give page not found for other failures


@login_required
def notify(request, user, ws_id):
    '''
    This function is volatile.It is only returns content when successful
    :param request:
    :param user:
    :param ws_id:
    :return:
    '''
    data=ws_id
    #glogger.debug("print websocketid:",data)
    request_data = request.POST if request.method == 'POST' else request.GET
    information=request_data['info']    
    #glogger.debug("data of notify: ",data)
    #callerId=data.values()[1]
    #meetingURL=data.values()[2]	
    notification_string = json.dumps(request_data)
    if attendance_register.hexists(ONLINE, ws_id):
        Channel(ws_id).send({'text':information})
        return HttpResponse(notification_string)
    else:
        return HttpResponseNotFound(settings.WS_OFFLINE_NOTICE)

@login_required
def notify_status(request, user, status):
    request_data = request.POST if request.method == 'POST' else request.GET
    information=request_data['info']
    receivers=request_data['receivers']
    receivers=json.loads(receivers)
    response={}

    for receiver in receivers:

        if attendance_register.hexists(ONLINE, receiver):
            #info={} 
            if status == 'call':
                _receivers=receivers[:]
                _receivers.remove(receiver) 
                info={}
                info['info']=information
                info['receivers']=_receivers
            else:
                info={}
                info['info']=json.dumps({'status':'disconnect','anotherLogin':'yes'})
            Channel(receiver).send({'text':json.dumps(info)})
            response[receiver]="Success"
        else:
            response[receiver]="Offline"
     
    return HttpResponse(json.dumps(response))

