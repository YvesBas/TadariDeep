library(data.table)
library(tuneR)
library(seewave)

f2pPF <- function(x) #get date-time data from recording file names
{
  if (is(x)[1] == "data.frame") {pretemps <- vector(length = nrow(x))}
  op <- options(digits.secs = 3)
  pretemps <- paste(substr(x, nchar(x) - 18, nchar(x)-4), ".", substr(x, nchar(x) - 2, nchar(x)), sep = "")
  strptime(pretemps, "%Y%m%d_%H%M%OS",tz="UTC")-0
}

HourSelected=c(c(21:23),c(0:4))
Predictions=fread("E:/ExportVigieChiro/Col_de_Bardou_Ht_Languedoc/SortiesTadariDeep/predictions_390911_96_390530_VigieChiroTest1.csv")
#Summary=fread("E:/ExportVigieChiro/Col_de_Bardou_Ht_Languedoc/SortiesTadariDeep/resume_par_cri_390911_96_390530_VigieChiroTest1.csv")
DirWav="E:/ExportVigieChiro/Col_de_Bardou_Ht_Languedoc"
Silence=1
Exp=T #TRUE si expansion de temps x10
FileOut="E:/ExportVigieChiro/Col_de_Bardou_Ht_Languedoc_concatene.wav"

Predictions$time=f2pPF(Predictions$`fichier wav`)
Predictions$hour=hour(Predictions$time)
barplot(table(Predictions$hour))

table(Predictions$`classe predite`)
boxplot(Predictions$Erirub)
boxplot(Predictions$Turphi)


Pred_HourSel=subset(Predictions,Predictions$hour %in% HourSelected)

table(Pred_HourSel$`classe predite`)
boxplot(Pred_HourSel$Erirub)
boxplot(Pred_HourSel$Turphi)

ListWav_Sel=unique(Pred_HourSel$`fichier wav`)

Wlist=list.files(DirWav,pattern=".wav$",full.names=T,recursive=T)
WTBC=subset(Wlist,basename(Wlist) %in% paste0(ListWav_Sel,".wav"))

W1=readWave(WTBC[1])
print(WTBC[1])
if(Exp){W1@samp.rate=W1@samp.rate*10}

InfoDSE=tstrsplit(Pred_HourSel$`fichier jpg`,split="--")
Pred_HourSel$Dur=as.numeric(InfoDSE[[4]])/1000
Pred_HourSel$FreqMP=as.numeric(InfoDSE[[5]])

Pred_HourSel$t2=(Pred_HourSel$t1+Pred_HourSel$Dur)
if(length(InfoDSE)>6){
  Pred_HourSel$t1=as.numeric(InfoDSE[[6]])/1000
  Pred_HourSel$fmin=as.numeric(InfoDSE[[7]])
  Pred_HourSel$fmax=as.numeric(InfoDSE[[8]])
}else{
  Pred_HourSel$t1=as.numeric(gsub(".jpg","",InfoDSE[[6]]))/1000
  Pred_HourSel$fmin=Pred_HourSel$FreqMP
  Pred_HourSel$fmax=Pred_HourSel$FreqMP
}
Pred_HourSel$Label=paste(Pred_HourSel$`classe predite`,Pred_HourSel$`pourcentage prediction`," - ",Pred_HourSel$FreqMP)
Pred1=subset(Pred_HourSel
             ,paste0(Pred_HourSel$`fichier wav`,".wav")==basename(WTBC[1]))
M1=subset(Pred1,select=c("Label","t1","t2","fmin","fmax"))

Wall=W1
Mall=M1
if(length(WTBC)>1){
  for (i in 2:length(WTBC)){
    Time=length(Wall@left)/Wall@samp.rate+Silence
    print(WTBC[i])
    Wi=readWave(WTBC[i])
    print(Wi@samp.rate)
    if(Exp){Wi@samp.rate=Wi@samp.rate*10}
    Inti=silence(duration=Silence*Wi@samp.rate,samp.rate = Wi@samp.rate,bit=Wi@bit,pcm=T)
    Wlist=list(Wall,Inti,Wi)
    Wall=do.call(tuneR::bind,Wlist)
    
    Predi=subset(Pred_HourSel
                 ,paste0(Pred_HourSel$`fichier wav`,".wav")==basename(WTBC[i]))
    Mi=subset(Pred1,select=c("Label","t1","t2","fmin","fmax"))
    Mi$t1=Mi$t1+Time
    Mi$t2=Mi$t2+Time
    Mall=rbind(Mall,Mi)
  }
}

writeWave(Wall,filename=FileOut,extensible=F) #ecrit le nouveau fichier wave
print(length(Wall@left)/Wall@samp.rate)
names(Mall)=c("label","t1","t2","f1","f2")
write.audacity(Mall,gsub(".wav","_td.txt",FileOut))


