from django.http import JsonResponse
from django.shortcuts import redirect,render
from app.models import slider,banner_area,Main_Category,Product,Category,Color,Brand,Coupon_Code
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.db.models import Max, Min, Sum
from cart.cart import Cart
from django.core.mail import send_mail

def BASE(request):
    return render(request,'base.html')

def HOME(request):
    sliders = slider.objects.all()
    banners = banner_area.objects.all()
    main_category = Main_Category.objects.all()
    product = Product.objects.filter(section__Name = 'Top Deals Of The Day')

    context = {
        'sliders':sliders,
        'banners':banners,
        'main_category':main_category,
        'product':product,
    }
    return render(request,'Main/home.html',context)

def PRODUCT_DETAILS(request,slug):
    product = Product.objects.filter(slug = slug)
    if product.exists():
        product = Product.objects.get(slug = slug)
    else:
        return redirect('404')
    context = {
        'product':product,
    }
    return render(request,"product/product_detail.html",context)

def Error404(request):
    return render(request,'errors/404.html')

def MY_ACCOUNT(request):
    return render(request,'account/my-account.html')

def REGISTER(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username = username).exists():
            messages.error(request,"Username already exists")
            return redirect('login')
        
        if User.objects.filter(email = email).exists():
            messages.error(request,"Email Id already exists")
            return redirect('login')
        
        user = User(
            username = username,
            email = email,
        )
        user.set_password(password)
        user.save()
        return redirect('login')
    return render(request,'login.html')

def LOGIN(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user  = authenticate(request,username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"Email and Password are Invalid !")
            return redirect('login')
    return render(request,'login.html')

@login_required(login_url='/accounts/login/')
def PROFILE(request):
    return render(request,'profile/profile.html')

@login_required(login_url='/accounts/login/')
def PROFILE_UPDATE(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_id = request.user.id

        user = User.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email

        if password != None and password != "":
            user.set_password(password)
        user.save()
        messages.success(request,"Profile Successfully Updated!")
    return redirect('profile')

def ABOUT(request):
    return render(request,'Main/about.html')

def CONTACT(request):
    return render(request,'Main/contact.html')

def PRODUCT(request):
    category = Category.objects.all()
    color = Color.objects.all()
    min_price = Product.objects.all().aggregate(Min('price'))
    max_price = Product.objects.all().aggregate(Max('price'))
    ColorID = request.GET.get('colorID')
    FilterPrice = request.GET.get('FilterPrice')
    brand = Brand.objects.all()

    if FilterPrice:
        Int_FilterPrice = int(FilterPrice)
        product = Product.objects.filter(price__lte = Int_FilterPrice)
    elif ColorID:
        product = Product.objects.filter(color = ColorID)
    else:
        product = Product.objects.all()


    context = {
        "category":category,
        "product":product,
        "min_price":min_price,
        "max_price":max_price,
        "FilterPrice":FilterPrice,
        "color":color,
        "brand":brand,
    }
    return render(request,'product/product.html',context)


def filter_data(request):
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    brand = request.GET.getlist('brand[]')

    allProducts = Product.objects.all().order_by('-id').distinct()
    if len(categories) > 0:
        allProducts = allProducts.filter(Categories__id__in=categories).distinct()

    if len(brands) > 0:
        allProducts = allProducts.filter(Brand__id__in=brands).distinct()


    t = render_to_string('ajax/product.html', {'product': allProducts})

    return JsonResponse({'data': t})

def CART(request):
    return render(request,'cart/cart.html')

@login_required(login_url="/accounts/login/")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")
@login_required(login_url="/accounts/login/")
def cart_detail(request):
    cart = request.session.get('cart')
    
    packing_cost = sum(i['packing_cost'] for i in cart.values() if i)
    tax = sum(i['tax'] for i in cart.values() if i)
    valid_coupon = None
    coupon = None
    invalid_coupon = None
    if request.method == 'GET':
        coupon_code = request.GET.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon_Code.objects.get(code = coupon_code)
                valid_coupon = "Are Applicable on Current Order !"
            except:
                invalid_coupon = "Invalid Coupon Code !"

    context={
        'packing_cost':packing_cost,
        'tax':tax,
        'coupon':coupon,
        'valid_coupon':valid_coupon,
        'invalid_coupon':invalid_coupon,
    }
    return render(request, 'cart/cart.html',context)

def CHECKOUT(request):
    cart = request.session.get('cart')
    packing_cost = sum(i['packing_cost'] for i in cart.values() if i)
    tax = sum(i['tax'] for i in cart.values() if i)
    valid_coupon = None
    coupon = None
    invalid_coupon = None
    if request.method == 'GET':
        coupon_code = request.GET.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon_Code.objects.get(code = coupon_code)
                valid_coupon = "Are Applicable on Current Order !"
            except:
                invalid_coupon = "Invalid Coupon Code !"
    context={
        'packing_cost':packing_cost,
        'tax':tax,
        'coupon':coupon,
        'valid_coupon':valid_coupon,
        'invalid_coupon':invalid_coupon,
    }
    return render(request,'checkout/checkout.html',context)

def SCANNER(request):
    return render(request,'scanner/scanner.html')