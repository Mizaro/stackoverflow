from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import Product, Brand
from django.db.models import Q


def search(request):
    queryset_list = Product.objects.order_by('price')
    # Keyworks
    if 'search' in request.GET:
        search = request.GET['search']

        if search:
            queryset_list = queryset_list.filter(Q(name__icontains=search) | Q(description__icontains=search))
            path = request.path
            link = path + '?' + 'search=' + search

            # Brands filter
            brands_list = []
            for query in queryset_list:
                if query.brand.name not in brands_list:
                    brands_list.extend([query.brand.name])
            brand_urls = {}
            brand_active = [False] * len(brands_list)
            if 'brand' not in request.GET:
                for brand in brands_list:
                    brand_urls[brand] = link + '&' + 'brand=' + brand
            else:
                active_filters = [f for f in request.GET['brand'].split(',')]
                if len(active_filters) > 1:
                    queryset_list = queryset_list.filter(brand__name__in=active_filters)
                for k, brand in enumerate(brands_list):
                    new_active_filters = active_filters.copy()

                    if brand in new_active_filters:
                        brand_active[k] = True
                        new_active_filters.remove(brand)
                        brand_urls[brand] = link + '&' + 'brand=' + ','.join(new_active_filters)
                    else:
                        brand_active[k] = False
                        new_active_filters.append(brand)
                        brand_urls[brand] = link + '&' + 'brand=' + ','.join(new_active_filters)

    paginator = Paginator(queryset_list, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'values': request.GET,
        'brand_urls': brand_urls,
        'brand_active': brand_active,
    }
    return render(request, 'products/search.html', context)