"""Opt-in original-prop operations; absent actions leave accepted Java identical."""
from .original_objects import targets,BITS
from .generator import java_string as js


def extend(java,campaign,scene):
    selected=targets(scene)
    if not selected:return java
    count=len(selected);lines=[f' private boolean[] originalApplied=new boolean[{count}], originalReported=new boolean[{count}];']
    lines+=[' private int originalFlag(int i,int bit) { switch(i) {']
    for i,k in enumerate(selected):
        values=[campaign.reserved['original/'+scene['id']+'/'+k+'/'+b] for b in BITS]
        lines.append(f' case {i}: switch(bit) {{ '+''.join(f'case {b}: return {v};' for b,v in enumerate(values))+' } break;')
    lines+=[' } return -1; }',' private boolean originalBit(int i,int bit) { return CodexSequence.GetChronicleFlag(originalFlag(i,bit)); }',' private void originalSet(int i,int bit,boolean value) { if(value) CodexSequence.SetChronicleFlag(originalFlag(i,bit)); else CodexSequence.ClearChronicleFlag(originalFlag(i,bit)); }',
            ' private boolean originalError(int i,String reason) { if(!originalReported[i]) { trace("ORIGINAL_FAILED "+i+" "+reason); originalReported[i]=true; } return false; }',
            ' private boolean originalNear(float[] p,double x,double y,double z) { if(p==null || p.length<3) return false; double dx=p[0]-x,dy=p[1]-y,dz=p[2]-z; return dx*dx+dy*dy+dz*dz<=64.0; }',
            ' private boolean originalMatches(int i,int guid) { if(!IsPropGuid(guid) || !local(guid) || guid==GetGUID()) return false; for(int n=0;n<things.length;n++) if(things[n]==guid) return false; CodexThing item=new CodexThing(guid); switch(i) {']
    for i,t in enumerate(selected.values()):
        clause=''
        if not t.get('cast_id'):
            x,y,z=t['position'];args=f'{float(x)},{float(y)},{float(z)}';clause=f' return originalNear(item.GetPosition(),{args}) || (item.HasFrames() && item.GetNumFrames()>0 && originalNear(item.GetFramePosition(0),{args}));'
        else:clause=' return true;'
        lines.append(f' case {i}: {{ if(!{js(t["template"])}.equalsIgnoreCase(item.GetTemplateName())) return false;'+clause+' }')
    lines+=[' } return false; }',' private int originalFind(int i) { switch(i) {']
    for i,t in enumerate(selected.values()):
        if t.get('cast_id'):lines.append(f' case {i}: {{ int g=CodexThing.GuidFromCastID({js(t["cast_id"])}); return originalMatches(i,g)?g:0; }}')
    lines+=[' } int found=0,g=new CodexWorld(WORLD_CURRENT).GetFirstThing(),steps=0; while(g!=0 && steps++<10000) { if(originalMatches(i,g)) { if(found!=0) return -1; found=g; } int next=new CodexThing(g).NextInWorld(); if(next==g) return -1; g=next; } return g==0?found:-1; }',
            ' private boolean originalApply(int i,int operation,int frame,float parameter,boolean opening) {',
            ' if(operation==1 && originalBit(i,6)) return originalError(i,"removed objects cannot be restored; use hide for reversible changes");',
            ' int guid=originalFind(i); if(guid<0) return originalError(i,"ambiguous identity or scan limit"); if(guid==0) { if(operation==2 && originalBit(i,6)) { originalApplied[i]=true; return true; } return originalError(i,"missing/local/template identity"); } CodexThing item=new CodexThing(guid);',
            ' if(operation>=3) { if(!item.HasFrames() || item.GetNumFrames()<=frame) return originalError(i,"missing frame"); boolean ok=operation==3?item.MoveToFrame(frame,parameter):item.RotatePivot(frame,opening?parameter:-parameter); if(!ok) return originalError(i,"engine rejected motion"); originalReported[i]=false; trace("ORIGINAL_DOOR "+i); return true; }',
            ' if(operation==2) { if(!item.Remove()) return originalError(i,"engine rejected removal"); originalSet(i,6,true); originalSet(i,5,false); originalApplied[i]=true; originalReported[i]=false; trace("ORIGINAL_REMOVE "+i); return true; }',
            ' if(!originalBit(i,0)) { originalSet(i,1,(item.GetRenderFlags()&THING_RENDERFLAG_DONTRENDER)!=0); originalSet(i,2,(item.GetThingFlags()&THING_FLAG_DISABLECOLLIDE)!=0); originalSet(i,3,(item.GetThingFlags()&THING_FLAG_VISBLOCK)!=0); originalSet(i,4,(item.GetThingFlags()&THING_FLAG_CAMERABLOCK)!=0); originalSet(i,0,true); }',
            ' if(operation==0) { item.SetRenderFlags(THING_RENDERFLAG_DONTRENDER); item.SetThingFlags(THING_FLAG_DISABLECOLLIDE); item.ClearThingFlags(THING_FLAG_VISBLOCK|THING_FLAG_CAMERABLOCK); originalSet(i,5,true); }',
            ' else { if(originalBit(i,1)) item.SetRenderFlags(THING_RENDERFLAG_DONTRENDER); else item.ClearRenderFlags(THING_RENDERFLAG_DONTRENDER); int[] masks=new int[]{THING_FLAG_DISABLECOLLIDE,THING_FLAG_VISBLOCK,THING_FLAG_CAMERABLOCK}; for(int b=0;b<3;b++) { if(originalBit(i,b+2)) item.SetThingFlags(masks[b]); else item.ClearThingFlags(masks[b]); } originalSet(i,5,false); }',
            ' originalApplied[i]=true; originalReported[i]=false; trace("ORIGINAL_STATE "+i+" "+operation); return true; }',
            ' private void originalReapply() { for(int i=0;i<originalApplied.length;i++) if(!originalApplied[i] && (originalBit(i,0)||originalBit(i,6))) originalApply(i,originalBit(i,6)?2:originalBit(i,5)?0:1,0,1.0f,true); }']
    marker='private void pollImpl() {'
    if java.count(marker)!=1:raise ValueError('Original object runtime integration is ambiguous')
    java=java.replace(marker,marker+' originalReapply();')
    marker='public void restored(int capture) {'
    if java.count(marker)!=1:raise ValueError('Original object restore integration is ambiguous')
    java=java.replace(marker,marker+' for(int i=0;i<originalApplied.length;i++) originalApplied[i]=false;')
    end=java.rfind('}')
    return java[:end]+'\n'+'\n'.join(lines)+'\n'+java[end:]
