from flask_caching import Cache

# Generamos la configuración de la caché
cache = Cache(config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})