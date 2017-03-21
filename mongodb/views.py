#coding=UTF-8
from django.shortcuts import render,render_to_response
from myapp.form import AddForm
# from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse
import mongo
from django.contrib.auth.decorators import login_required,permission_required
from myapp.include import function as func

# Create your views here.
@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_query_mongo', login_url='/')
def mongodb_query(request):
    try:
        favword = request.COOKIES['myfavword']
    except Exception,e:
        pass
    dblist = mongo.get_mongodb_list(request.user.username)
    #dblist = ['ymmSmsLogYm','table2','table3','table4']
    if request.method == 'POST' :
        form = AddForm(request.POST)

            #instancetag = request.POST['instancetag']
        choosedb = request.POST['choosedb']
        tblist = mongo.get_mongo_collection(choosedb, request.user.username)
        try:
            if request.POST.has_key('gettblist'):

                return render(request, 'mongodb_query.html', locals())
            elif request.POST.has_key('query'):
                #return HttpResponse(tablename)
                choosed_tb = request.POST['choosed_tb']
                if form.is_valid():
                    a = form.cleaned_data['a']
                    func.log_mongo_op(a,choosedb,choosed_tb,request)
                    data_list = mongo.get_mongo_data(a, choosedb, choosed_tb, request.user.username)
                # print data_list
                return render(request,'mongodb_query.html',locals())
            elif request.POST.has_key('dbinfo'):
                del tblist
                info = mongo.get_db_info(choosedb, request.user.username)
                return render(request, 'mongodb_query.html', locals())
            elif request.POST.has_key('tbinfo'):
                choosed_tb = request.POST['choosed_tb']
                info = mongo.get_tb_info(choosedb,choosed_tb, request.user.username)
                return render(request, 'mongodb_query.html', locals())
            elif request.POST.has_key('tbindexinfo'):
                choosed_tb = request.POST['choosed_tb']
                indinfo = mongo.get_tbindex_info(choosedb, choosed_tb, request.user.username)
                # print info
                return render(request, 'mongodb_query.html', locals())

                # return render(request,'mongodb_query.html',{'form': form,'data_list':data_mongo,'col':"record",'tablelist':table_list,'choosed_table':tablename})
        except Exception,e:
            print e
            return render(request, 'mongodb_query.html', locals())
            #else:
                #return render(request, 'mongo_query.html', {'form': form })
        # else:
        #     print "not valid"
        #     return render(request, 'mongodb_query.html', locals())
    else:
        form = AddForm()
        return render(request, 'mongodb_query.html', locals())


def map(request):
    mysrc = "http://api.map.baidu.com/api?v=2.0&ak=zhskfLsPCGPrPQvGb2WsL2mGZsfGO9XT&callback=initialize"
    return render(request, 'map.html', locals())