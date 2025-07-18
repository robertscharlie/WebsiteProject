from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
import sys
import django
from django.conf import settings
import os
import platform
import time
import psutil


# Create your views here.

@login_required(login_url='login')
def serverViewPage(request):
    # Python & Django
    python_version = sys.version.split()[0]
    django_version = django.get_version()
    debug_mode = settings.DEBUG
    installed_apps = settings.INSTALLED_APPS

    # Database
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']

    # Server & OS
    os_name = os.name
    os_version = platform.version()
    machine = platform.machine()
    processor = platform.processor()
    hostname = platform.node()
    platform_name = platform.system()
    architecture = platform.architecture()[0]
    release = platform.release()
    cpu_count = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    cpu_freq_mhz = int(cpu_freq.current) if cpu_freq else None
    cpu_usage_percent = psutil.cpu_percent(interval=0.1)

    # Memory
    mem = psutil.virtual_memory()
    memory_total_mb = int(mem.total / 1024 / 1024)
    memory_used_mb = int(mem.used / 1024 / 1024)
    memory_available_mb = int(mem.available / 1024 / 1024)
    memory_percent = mem.percent

    # Disk
    disk = psutil.disk_usage('/')
    disk_total_gb = round(disk.total / 1024 / 1024 / 1024, 2)
    disk_used_gb = round(disk.used / 1024 / 1024 / 1024, 2)
    disk_free_gb = round(disk.free / 1024 / 1024 / 1024, 2)
    disk_percent = disk.percent

    # Network
    ip_addresses = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == getattr(psutil, 'AF_INET', 2):
                ip_addresses.append(addr.address)
    network_io = psutil.net_io_counters()
    network_io_sent_mb = round(network_io.bytes_sent / 1024 / 1024, 2)
    network_io_recv_mb = round(network_io.bytes_recv / 1024 / 1024, 2)

    # Django/Server Uptime
    if not hasattr(serverViewPage, '_start_time'):
        serverViewPage._start_time = time.time()
    django_server_uptime_seconds = int(time.time() - serverViewPage._start_time)
    django_server_uptime_string = time.strftime('%H:%M:%S', time.gmtime(django_server_uptime_seconds))

    # System Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    uptime_string = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
    boot_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time))

    # Django Settings
    allowed_hosts = settings.ALLOWED_HOSTS
    time_zone = settings.TIME_ZONE
    static_url = settings.STATIC_URL
    media_url = getattr(settings, 'MEDIA_URL', '')

    context = {
        'python_version': python_version,
        'django_version': django_version,
        'debug_mode': debug_mode,
        'installed_apps': installed_apps,
        'db_engine': db_engine,
        'db_name': db_name,
        'os': os_name,
        'os_version': os_version,
        'machine': machine,
        'processor': processor,
        'hostname': hostname,
        'platform': platform_name,
        'architecture': architecture,
        'release': release,
        'cpu_count': cpu_count,
        'cpu_freq_mhz': cpu_freq_mhz,
        'cpu_usage_percent': cpu_usage_percent,
        'memory_total_mb': memory_total_mb,
        'memory_used_mb': memory_used_mb,
        'memory_available_mb': memory_available_mb,
        'memory_percent': memory_percent,
        'disk_total_gb': disk_total_gb,
        'disk_used_gb': disk_used_gb,
        'disk_free_gb': disk_free_gb,
        'disk_percent': disk_percent,
        'ip_addresses': ip_addresses,
        'network_io_sent_mb': network_io_sent_mb,
        'network_io_recv_mb': network_io_recv_mb,
        'django_server_uptime_seconds': django_server_uptime_seconds,
        'django_server_uptime_string': django_server_uptime_string,
        'uptime_seconds': uptime_seconds,
        'uptime_string': uptime_string,
        'boot_time': boot_time_str,
        'allowed_hosts': allowed_hosts,
        'time_zone': time_zone,
        'static_url': static_url,
        'media_url': media_url,
    }

    return render(request, 'serverInfo/serverInfo.html', context)

