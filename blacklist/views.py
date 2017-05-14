from django.shortcuts import render
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from blacklist.models import Tb_blacklist
from django.contrib.auth.decorators import login_required,permission_required
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse,JsonResponse


# Create your views here.

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_set_pri', login_url='/')
def blist(request):
    page_size = 10
    all_record = Tb_blacklist.objects.all().order_by('id')
    paginator = Paginator(all_record, page_size)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blist.html', locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_set_pri', login_url='/')
def bl_delete(request):
    try:
        myid = int(request.GET['dbid'])
        db = Tb_blacklist.objects.get(id=myid)
        db.delete()
    except:
        pass
    finally:
        return HttpResponseRedirect("/blacklist/blist/")

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_set_pri', login_url='/')
def bl_edit(request):

    return render(request, 'bl_edit.html', locals())