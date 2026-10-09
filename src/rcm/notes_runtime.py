"""Local native text UI ownership and deferred textended callback."""
def extend_notes(java):
    def replace(old,new):
        nonlocal java
        if java.count(old)!=1:raise ValueError('Notas: integración ausente o ambigua: '+old)
        java=java.replace(old,new)
    guard='if(active!=-1 || pendingDialogueEnd || cameraTicks>0 || !IsPlayerGuid(player))' if 'if(active!=-1 || pendingDialogueEnd || cameraTicks>0 || !IsPlayerGuid(player))' in java else 'if(active!=-1 || pendingDialogueEnd || !IsPlayerGuid(player))'
    replace(guard,guard.replace('if(','if(notePlayer!=0 || pendingNoteEnd || ',1))
    replace('if(NetIsClient()||active!=-1||pendingDialogueEnd||',
            'if(NetIsClient()||notePlayer!=0||pendingNoteEnd||active!=-1||pendingDialogueEnd||')
    replace('player=clicker;', 'player=clicker; noteOrigin=target;')
    replace('if(player!=0 && active==-1 && !pendingDialogueEnd && !transitioning)',
            'if(player!=0 && notePlayer==0 && !pendingNoteEnd && active==-1 && !pendingDialogueEnd && !transitioning)')
    replace('finishDialogue(); if(transitioning) return;', 'finishNote(); finishDialogue(); if(transitioning) return;')
    replace('public void restored(int capture) {','public void restored(int capture) { notePlayer=0; noteOrigin=0; pendingNoteEnd=false;')
    methods='''
 private int notePlayer=0,noteOrigin=0; private boolean pendingNoteEnd=false;
 private boolean showNote(String name) {
 if(NetIsClient() || notePlayer!=0 || pendingNoteEnd || active!=-1 || pendingDialogueEnd || cameraTicks>0 || !IsPlayerGuid(player)) return false;
 int who=player; notePlayer=who; holdPatrols(); boolean ok=false;
 try { ok=ExecuteText(who,local(noteOrigin)?noteOrigin:0,name); } catch(Throwable error) { trace("NOTE_FAILED "+error); }
 if(!ok) { notePlayer=0; pendingNoteEnd=false; resumePatrols(); trace("NOTE_FAILED "+name); }
 else trace("NOTE_OPEN "+name); noteOrigin=0; return ok;
 }
 public void textended(int who) { if(notePlayer==0 || who!=notePlayer || pendingNoteEnd) return; pendingNoteEnd=true; schedulePoll(); }
 private void finishNote() { if(!pendingNoteEnd) return; int who=notePlayer; notePlayer=0; pendingNoteEnd=false; resumePatrols(); if(!NetIsClient() && localPlayer(who)==who) { player=who; trace("NOTE_CLOSED"); dispatch("note_closed","",0); } }
'''
    return java[:-2]+methods+'\n}\n'
