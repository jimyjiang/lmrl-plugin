# shared_phantom.py
import sublime
import threading

_phantom_sets = {}  # 存储各视图的PhantomSet
_update_timer_set = {}

def get_phantom_set(view):
    view_id = view.id()
    if view_id not in _phantom_sets:
        _phantom_sets[view_id] = sublime.PhantomSet(view, "global_shared_phantom")
    return _phantom_sets[view_id]

def set_timeout_async(view, callback, timeout):
    view_id = view.id() 
    timer = threading.Timer(timeout, callback)
    _update_timer_set[view_id] = timer
    timer.start()

    
def clean_tiimeout(view):
    view_id = view.id() 
    if view_id in _update_timer_set:
        timer = _update_timer_set[view_id]
        if timer is not None:
            timer.cancel()
        del _update_timer_set[view_id]

def clear_all_phantoms():
    for phantom_set in _phantom_sets.values():
        phantom_set.update([])
    _phantom_sets.clear()
    clean_tiimeout()

def clear_phantom_set(view):
    view_id = view.id()
    clean_tiimeout(view)
    if view_id in _phantom_sets:
        phantom_set = _phantom_sets[view_id]
        phantom_set.update([]) 
        del _phantom_sets[view_id]
