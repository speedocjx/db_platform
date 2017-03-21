from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required,permission_required

from myapp.include import  meta
# Create your views here.
@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_mysqladmin', login_url='/')
def dbstatus(request):
    try:
        xaxis = []
        yaxis = []
        choosed_host = request.GET['dbtag']
        days_before = int(request.GET['day'])
        if days_before not in [7,15,30]:
            days_before = 7
        if choosed_host!='all':
            data_list, col = meta.get_hist_dbinfo(choosed_host,days_before)
        elif choosed_host == 'all':
            return JsonResponse({'xaxis': ['not support all'], 'yaxis': [1]})
        for i in data_list:
            xaxis.append(i[0])
            yaxis.append(i[1])
        mydata = {'xaxis':xaxis,'yaxis':yaxis}
    except Exception,e:
        print e
        mydata = {'xaxis': ['error'], 'yaxis': [1]}
    return JsonResponse(mydata)


@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_metadata', login_url='/')
def tb_inc_status(request):
    xaxis7 = []
    yaxis7 = []
    xaxis15 = []
    yaxis15 = []
    xaxis30 = []
    yaxis30 = []
    choosed_host = request.GET['dbtag']
    tbname = request.GET['tbname'].strip()
    data_list7, col7 = meta.get_hist_tbinfo(choosed_host,tbname,7)
    data_list15,col15 = meta.get_hist_tbinfo(choosed_host,tbname,15)
    data_list30, col30 = meta.get_hist_tbinfo(choosed_host, tbname, 30)
    for i in data_list7:
        xaxis7.append(i[0])
        yaxis7.append(i[1])
    for i in data_list15:
        xaxis15.append(i[0])
        yaxis15.append(i[1])
    for i in data_list30:
        xaxis30.append(i[0])
        yaxis30.append(i[1])
    return JsonResponse({'xaxis7': xaxis7, 'yaxis7': yaxis7,'xaxis15': xaxis15, 'yaxis15': yaxis15,'xaxis30': xaxis30, 'yaxis30': yaxis30})