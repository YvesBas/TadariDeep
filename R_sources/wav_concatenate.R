library(tuneR)

DirW="D:/PourPablo"
DirOut="D:/PourPabloConc"
LW=list.files(DirW,pattern=".wav$",full.names=T)
RatioCorrectionTemps=10

dir.create(DirOut)

Pref=substr(basename(LW),1,24)

ListPref=unique(Pref)

for (i in 1:length(ListPref)){
  print(i)
  print(Sys.time())
  Wi=subset(LW,Pref==ListPref[i])
  
  Wlist=list()
  for (j in 1:length(Wi)){
    #for (i in 1:length(LW)){
    Wlist[[j]]=readWave(Wi[j])
    #print(class(Wlist[[i]]))
  }
    Wbig=do.call(tuneR::bind,Wlist)
    Wbig@samp.rate=Wbig@samp.rate*RatioCorrectionTemps
    
    writeWave(Wbig,filename=paste0(DirOut,"/",basename(Wi[1])),extensible=F) #ecrit le nouveau fichier wave
  
}
