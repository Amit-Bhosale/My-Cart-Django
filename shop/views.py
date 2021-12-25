from django.shortcuts import render
from django.http import HttpResponse
import json,math
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil

# Create your views here.
def index(request):
    products=Product.objects.all()
    print(products)
    allProds=[]
    catprods=Product.objects.values('category','id')
    cats={items['category']for items in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod,range(0,nSlides),nSlides])
    params = {'allProds': allProds}
    return render(request,'shop/index.html',params)


def about(request):
    return render(request,'shop/about.html')




def contact(request):
    if request.method=='POST':
        name= request.POST.get('name','')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('message', '')
        print(name,email,phone,desc)
        contact=Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
        submit = True
        return render(request, 'shop/contact.html', {'submit': submit})
    return render(request,'shop/contact.html')

def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    elif query in item.desc or query in item.product_name or query in item.category :
        return True
    else:
        return False

def search(request):
    query=request.GET.get('search')
    products = Product.objects.all()
    print(products)
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {items['category'] for items in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod= [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(0, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query) < 4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request,'shop/search.html',params)



def productview(request,myid):
    product=Product.objects.filter(id=myid)
    print(product)
    return render(request,'shop/productview.html',{'product':product[0]})



def checkout(request):
    products = Product.objects.all()

    if request.method=='POST':
        print(request)
        items_json = request.POST.get('itemsJson', '')
        name= request.POST.get('name','')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '')+ " " +request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        Order=Orders(items_json=items_json,name=name,email=email,address=address,city=city,state=state,zip_code=zip_code,phone=phone)
        Order.save()
        update=OrderUpdate(order_id=Order.order_id,update_desc="Your Order Has  been Placed")
        update.save()
        thank=True
        id=Order.order_id
        return render(request, 'shop/checkout.html',{'thank':thank,'id':id,'products':products})
    return render(request,'shop/checkout.html')




def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('OrderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success","updates":updates,"itemsJson":order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')