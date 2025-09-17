from django.contrib import admin
from .models import MenuItem, Order, OrderItem, Customer, CompletedOrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('menu_item', 'quantity', 'status', 'preparation_time')
    readonly_fields = ('menu_item', 'quantity', 'status', 'preparation_time')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image')
    search_fields = ('name',)
    list_filter = ('price',)
    ordering = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'name', 'table_number', 'mobile_number', 'created_at')
    search_fields = ('name', 'table_number', 'mobile_number')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'status', 'preparation_time')
    list_filter = ('status',)
    search_fields = ('menu_item__name', 'order__name')
    ordering = ('order',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id',)

@admin.register(CompletedOrderItem)
class CompletedOrderItemAdmin(admin.ModelAdmin):
    list_display = ('completed_order', 'menu_item_name', 'quantity', 'price', 'status')
    list_filter = ('status',)
    search_fields = ('menu_item_name', 'completed_order__name')
    ordering = ('completed_order',)