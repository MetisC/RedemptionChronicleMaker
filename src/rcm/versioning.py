"""Compatibility ordering for stable and explicitly named prerelease versions."""
import re


def version_key(value):
    if not isinstance(value,str):raise ValueError('Invalid RCM version')
    match=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:-(alpha|beta|rc)([1-9]\d*))?',value)
    if not match:raise ValueError('Invalid RCM version: '+value)
    major,minor,patch=map(int,match.groups()[:3])
    stage=match[4]
    return major,minor,patch,{'alpha':0,'beta':1,'rc':2,None:3}[stage],int(match[5] or 0)
