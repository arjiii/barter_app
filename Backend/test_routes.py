import sys
sys.path.insert(0, '.')

try:
    from app.main import app
    print('App loaded successfully')
    print(f'Total routes: {len(app.routes)}')
    print('\nAll routes:')
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = list(route.methods) if hasattr(route, 'methods') else []
            print(f'  {route.path} - {methods}')
    
    # Check specifically for debug endpoint
    debug_routes = [r for r in app.routes if hasattr(r, 'path') and 'debug' in r.path.lower()]
    print(f'\nDebug routes found: {len(debug_routes)}')
    for route in debug_routes:
        print(f'  {route.path}')
        
except Exception as e:
    print(f'Error loading app: {e}')
    import traceback
    traceback.print_exc()


