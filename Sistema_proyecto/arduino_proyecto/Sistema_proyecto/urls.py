"""
URL configuration for Sistema_proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static
from .views import ComentarioOTCreateView,PresupuestoAceptarView,PresupuestoRechazarView,CondicionesTallerView,ReporteListView,FacturaDetailView, FacturaListView,OrdenCompraUpdateView,OrdenCompraDetailView,HomeView,QuienesSomosView,ServiciosView,UbicacionView, ContactoView,HerramientaListView, HerramientaCreateView, HerramientaDetailView,HerramientaUpdateView,HerramientaDeleteView,RegistroUsoListView,RegistroUsoCreateView,RegistroUsoDetailView, RegistroUsoUpdateView,RegistroUsoDeleteView,OrdenTrabajoListView, OrdenTrabajoDetailView, OrdenTrabajoUpdateView,  PresupuestoListView,PresupuestoCreateView,PresupuestoDetailView, PresupuestoUpdateView,OrdenCompraListView,OrdenCompraCreateView,TrabajadorListView,TrabajadorCreateView,TrabajadorUpdateView,TrabajadorDeleteView,DisponibilidadUpdateView
from Sistema_proyecto.views import factura_pdf, mostrar_factura
from . import views



urlpatterns = [


    #      PÁGINAS PÚBLICAS


    path('', views.inicio, name='inicio'),
    path('home/', HomeView.as_view(), name='home'),
    path('quienes-somos/', QuienesSomosView.as_view(), name='quienes_somos'),
    path('servicios/', ServiciosView.as_view(), name='servicios'),
    path('ubicacion/', UbicacionView.as_view(), name='ubicacion'),
    path('contacto/', ContactoView.as_view(), name='contacto'),
    path('cotizacion/', views.cotizacion_crear_view, name='cotizacion_crear'),
    path('correo/', views.enviar_correo, name='correo'),


    #          AUTENTICACIÓN

    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'), 


    #      PANEL ADMINISTRADOR


    path('administrador/dashboard/', views.dashboard_admin, name='home_admin'),
    path('administrador/informe-energia/', views.informe_energia, name='informe_energia'),
    path('administrador/perfil/', views.perfil_administrador, name='perfil_admin'),

    # PREDICCION
    path('api/prediccion/', views.api_prediccion, name='api_prediccion'),
    path('prediccion/', views.vista_prediccion, name='prediccion'),

    # Cotizaciones
    path('administrador/cotizaciones/', views.cotizaciones_admin, name='cotizacion_admin'),
    path('administrador/cotizacion/<int:id>/aceptar/', views.aceptar_cotizacion, name='aceptar_cotizacion'),
    path('administrador/cotizacion/<int:id>/rechazar/', views.rechazar_cotizacion, name='rechazar_cotizacion'),
    path('administrador/cotizacion/<int:pk>/detalle/', views.DetalleCotizacionView.as_view(), name='cotizacion_detalle'),
    path('administrador/cotizacion/<int:id>/listar/', views.cotizaciones_admin, name='cotizacion_admin'),

    # Exportaciones
    path('administrador/exportar-mediciones/', views.exportar_mediciones_excel, name='exportar_mediciones_excel'),
    path('administrador/exportar-informe/', views.exportar_informe_excel, name='exportar_informe_excel'),
    path('administrador/exportar-cotizaciones-pdf/', views.exportar_cotizaciones_pdf, name='exportar_cotizaciones_pdf'),
    path('administrador/respaldar-limpiar/', views.respaldar_y_limpiar, name='respaldar_y_limpiar'),
    path('administrador/limpiar-mediciones/', views.limpiar_mediciones, name='limpiar_mediciones'),
    path('exportar-ot-excel/<int:pk>/', views.exportar_ot_excel, name='exportar_ot_excel'),

    # Sensores e IoT
    path("", include("mediciones.urls")),
    path("", include("sensor.urls")),
    path("administrador/metabase/", views.metabase_embed, name="metabase_embed"),

    # Herramientas
    path("herramientas/", HerramientaListView.as_view(), name="lista_herramientas"),
    path("herramientas/crear/", HerramientaCreateView.as_view(), name="crear_herramienta"),
    path("herramientas/<int:pk>/", HerramientaDetailView.as_view(), name="detalle_herramienta"),
    path("Herramientas/<int:pk>/editar/", HerramientaUpdateView.as_view(), name="editar_herramienta"),
    path("herramientas/<int:pk>/eliminar/", HerramientaDeleteView.as_view(), name="eliminar_herramienta"),

    # Registro de Herramientas 
    path("herramientas/uso/", RegistroUsoListView.as_view(), name="lista_registros_uso"),
    path("herramientas/uso/crear/", RegistroUsoCreateView.as_view(), name="crear_registro_uso"),
    path("herramientas/uso/<int:pk>/", RegistroUsoDetailView.as_view(), name="detalle_registro_uso"),
    path("herramientas/uso/<int:pk>/editar/", RegistroUsoUpdateView.as_view(), name="editar_registro_uso"),
    path("herramientas/uso/<int:pk>/eliminar/", RegistroUsoDeleteView.as_view(), name="eliminar_registro_uso"),


    # Trabajadores
    path("trabajadores/", TrabajadorListView.as_view(), name="lista_trabajadores"),
    path("trabajadores/crear/", TrabajadorCreateView.as_view(), name="crear_trabajador"),
    path("trabajadores/<int:pk>/editar/", TrabajadorUpdateView.as_view(), name="editar_trabajador"),
    path("trabajadores/<int:pk>/eliminar/", TrabajadorDeleteView.as_view(), name="eliminar_trabajador"),
    path("trabajadores/<int:pk>/disponibilidad/", DisponibilidadUpdateView.as_view(), name="disponibilidad_trabajador"),

    # Ordenes de Trabajo
    path("ot/", OrdenTrabajoListView.as_view(), name="lista_ot"),
    path("ot/crear/<int:pk>/", views.crear_ot_desde_presupuesto, name="crear_ot"),
    path("ot/<int:pk>/", OrdenTrabajoDetailView.as_view(), name="detalle_ot"),
    path("ot/editar/<int:pk>/", OrdenTrabajoUpdateView.as_view(), name="editar_ot"),

    # Presupuesto 

    path("presupuestos/", PresupuestoListView.as_view(), name="lista_presupuestos"),
    path("presupuestos/crear/<int:cotizacion_id>/",  PresupuestoCreateView.as_view(), name="crear_presupuesto"),
    path("presupuestos/<int:pk>/", PresupuestoDetailView.as_view(), name="detalle_presupuesto"),
    path("presupuestos/<int:pk>/aceptar/", PresupuestoAceptarView.as_view(), name="presupuesto_aceptar"),
    path("presupuestos/<int:pk>/rechazar/", PresupuestoRechazarView.as_view(), name="presupuesto_rechazar"),
    path("presupuestos/<int:pk>/editar/", PresupuestoUpdateView.as_view(), name="editar_presupuesto"),
    path("presupuestos/reenviar/<int:pk>/", views.reenviar_presupuesto, name="presupuesto_reenviar"),


    # Ordenes de Compra

    path("oc/", OrdenCompraListView.as_view(), name="lista_oc"),
    path("oc/crear/<int:presupuesto_id>/", OrdenCompraCreateView.as_view(), name="crear_oc"),
    path("oc/<int:pk>/", OrdenCompraDetailView.as_view(), name="detalle_oc"),
    path("oc/<int:pk>/editar/", OrdenCompraUpdateView.as_view(), name="editar_oc"),

    # Facturas 
    path("ot/<int:pk>/finalizar/", views.finalizar_ot, name="finalizar_ot"),
    path("ot/<int:pk>/entregar/", views.entregar_ot, name="entregar_ot"),
    path("facturas/", FacturaListView.as_view(), name="lista_facturas"),
    path("factura/<int:pk>/pdf/", factura_pdf, name="factura_pdf"),
    path("facturas/", FacturaListView.as_view(), name="lista_facturas"),
    path("ot/<int:pk>/facturar/", views.facturar_ot, name="facturar_ot"),
    path("facturas/<int:pk>/", FacturaDetailView.as_view(), name="detalle_factura"),
    path("factura/<int:pk>/pdf/", views.factura_pdf, name="facturar_pdf"),
    path("factura/<int:pk>/mostrar/", mostrar_factura, name="mostrar_factura"),



    # Comentario
    path("ot/<int:ot_id>/comentario/agregar/", ComentarioOTCreateView.as_view(), name="agregar_comentario_ot"),

    # Taller
    path("taller/condiciones/", CondicionesTallerView.as_view(), name="lista_condicion_taller"),

    # Reportes
    path("reportes/metabase", views.metabase_embed, name="metabase_embed"),
    path("reportes/", ReporteListView.as_view(), name="lista_reportes"),
    path("administrador/reportes/", views.reportes_administrador, name="reportes_admin"),

    #Alertas
    path("admin/alertas/", views.alertas_lista, name="alertas_lista"),


    # ADMIN DE DJANGO

    path('admin/', admin.site.urls),
]


# ARCHIVOS STATIC & MEDIA  


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)