# landing/context_processors.py — переменные profile и fav_state доступны во всех шаблонах
from .accounts import Favorite, get_profile

KINDS = ('event', 'movie', 'tour', 'place', 'guide')


def auth_profile(request):
    user = getattr(request, 'user', None)
    state = {'authed': False}
    for k in KINDS:
        state[k] = []
    if user is None or not user.is_authenticated:
        return {'fav_state': state, 'fav_total': 0}
    state['authed'] = True
    for kind, oid in Favorite.objects.filter(user=user).values_list('kind', 'object_id'):
        if kind in state:
            state[kind].append(oid)
    return {
        'profile': get_profile(user),
        'fav_state': state,
        'fav_total': sum(len(state[k]) for k in KINDS),
    }
