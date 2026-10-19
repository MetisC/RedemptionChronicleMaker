"""Original clan/discipline definitions, with optional imported extension."""


def base_catalogue(ws,resources):
    from .wtd import _table
    from .project_resources import original_bytes
    def table(ext,width):
        entries=[e for e in resources['entries'] if e['path'].casefold()=='misc/game.'+ext and not e.get('imported_pack')]
        if len(entries)!=1:return {}
        return _table(original_bytes(ws,entries[0]),width)
    try:clans=table('ncd',29);powers=table('ndd',28)
    except FileNotFoundError:return {}
    except ValueError:
        if ws.game is None:return {}
        raise
    if not clans or not powers:return {}
    classes={e['id'] for e in resources['entries'] if e['extension']=='.class' and not e.get('imported_pack')}
    return dict(clans=[dict(id=v[0],groups=v[7:10],imported=False) for v in clans.values()],disciplines=[dict(id=v[0],group=v[1],script=v[3],imported=False) for v in powers.values() if v[3] in classes])


def catalogue(resources):return resources.get('wtd') or resources.get('base_traits',{})
