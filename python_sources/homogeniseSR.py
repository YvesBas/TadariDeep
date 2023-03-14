import librosa
import os
import soundfile

RSDB="D:/PourPabloConc" #dossier input
RSDBdirs=["D:\PourPabloResampled"] #dossiers output
SRs=[44100] #liste des taux d echantillonnage a realiser, doit correspondre dans l'ordre aux dossiers input
print('input success')

ListWav=[os.path.join(dp, f) for dp, dn, filenames in os.walk(RSDB) for f in filenames if os.path.splitext(f)[1] == '.wav']
#ListWav=os.listdir(RSDB)
#print(ListWav)
llw = len(ListWav)
print(llw)


for h in range(len(RSDBdirs)):
    DirResampl=RSDBdirs[h]
    MinSRs=SRs[h]
    os.makedirs(DirResampl,exist_ok = True)
  
    print(MinSRs)
  
    for i in range(llw):
        
        #print(i)
        #print(ListWav[i])
        #WavA=readWave(ListWav[i]) #lit le fichier wave
        y, s = librosa.load(ListWav[i], sr=SRs[h])
        NewName = ListWav[i].replace(RSDB,DirResampl)
        print(NewName)
        DirNN=os.path.dirname(NewName)
        print(DirNN)
        os.makedirs(DirNN,exist_ok=True)
        soundfile.write(data=y,file=NewName,samplerate=SRs[h])

print('end')
