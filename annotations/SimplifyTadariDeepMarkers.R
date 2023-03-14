library(seewave)
library(data.table)
library(stringr)

PredD=commandArgs(trailingOnly = T)

#PredD="C:/Users/yvesb/Documents/TadariDeep/TadariDeep_batch/sortie230202/"
WindowMax=5
ColFirstClass=10
Thres=0

PredFs=list.files(paste0(PredD,"/txtpred/"),pattern="predictions_",full.names=T,recursive=T)
#print(paste0(PredD,"/rwb.txt"))
rwbs=fread(paste0(PredD,"/rwb.txt"))

print(head(rwbs))

testV2=nchar(rwbs$V2)
uV2=unique(rwbs$V2)
uV2=gsub("G_","",uV2)

#print("L19")

for (i in 1:length(PredFs)){
  
  
  #print("L24")
  #print(PredFs[i])
  PredF=PredFs[i]
  Pred=fread(PredF)
  
  #if(sd(testV2)!=0){
  
  #print("L34")
  #print(c(Pred$`fichier wav`[1],uV2))
  PositionF1=str_order(c(uV2,Pred$`fichier wav`[1]))
  #print(PositionF1)
  
  #print(uV2[PositionF1[length(PositionF1)]-1])
  rwb=subset(rwbs,rwbs$V2==paste0("G_",uV2[PositionF1[length(PositionF1)]-1])) 
  
  # }else{
  #rwb=subset(rwbs,rwbs$V2==substr(Pred$`fichier wav`[1],1,testV2[1]))  
  # }
  #FileMarker=list.files(DirMarkers,pattern="tdauda",full.names=T)
  
  
  ClassList=names(Pred)[ColFirstClass:ncol(Pred)]
  OtherVariables=subset(names(Pred),!(names(Pred) %in% ClassList))
  
  InfoDSE=tstrsplit(Pred$`fichier jpg`,split="--")
  
  #print("L45")
  #print(head(Pred$`fichier jpg`))
  
  
  Pred$Amp=as.numeric(InfoDSE[[3]])
  Pred$Dur=as.numeric(InfoDSE[[4]])/1000
  Pred$FreqMP=as.numeric(InfoDSE[[5]])
  Pred$t1=as.numeric(InfoDSE[[6]])/1000
  Pred$t2=(Pred$t1+Pred$Dur)
  Pred$fmin=as.numeric(InfoDSE[[7]])
  Pred$fmax=as.numeric(InfoDSE[[8]])

  #print("L57")
  #print(head(Pred$t1))
  
  #print("L60")
  #print(head(rwb))
  
  testR=match(Pred$'fichier wav',rwb$V1)
  Pred$t1=Pred$t1+rwb$V3[testR]
  Pred$t2=Pred$t2+rwb$V3[testR]

  #print("L63")
  #print(head(Pred$t1))
  
  #print(head(Pred$Amp))  
  #plot(as.numeric(InfoDSE[[5]]),as.numeric(InfoDSE[[8]]))
  #plot(as.numeric(InfoDSE[[5]]),as.numeric(InfoDSE[[7]]))
  #plot(as.numeric(InfoDSE[[5]]),as.numeric(gsub(".jpg","",InfoDSE[[9]])))
  
  
  Pred=Pred[order(Pred$t1),]
  
  PredBackup=Pred
  
  #print("L66")
  Markers=subset(Pred,select=c("classe predite","t1","t2","fmin","fmax"))
  #print(dim(Markers))
  
  #print("L68")
  #print(nrow(Pred))
  MarkersSimplified=Markers[0,]
  while(nrow(Pred)>0){
    #class(Pred$t1)
    #print(Pred$t1)
    #print(WindowMax)
    Min=subset(Pred,Pred$t1<Pred$t1[1]+WindowMax)  
    Mout=subset(Pred,Pred$t1>=Pred$t1[1]+WindowMax)  
    #print(dim(Min))
    #print(ClassList)
    Mprob=subset(Min,select=ClassList)
    #print("L75")
    #print(dim(Mprob))
    MaxparFich=max(Mprob)  
    #find the most probable species in each file
    CallScores=apply(Mprob,1,max)
    CallMax=which(CallScores==MaxparFich)
    #print(CallMax)
    SpSel=apply(Mprob[CallMax,],1,which.max)
    SpSelName=ClassList[SpSel]
    print(paste(SpSelName,MaxparFich))
    Minsel=subset(Min,as.data.frame(Mprob)[,SpSel]>1)  
    Minout=subset(Min,as.data.frame(Mprob)[,SpSel]<=1)  
    #remaining data
    Pred=rbind(Minout,Mout)
    #compute the selected marker
    Labeli=paste(SpSelName,MaxparFich)
    t1i=min(Minsel$t1)
    t2i=max(Minsel$t2)
    f1i=min(Minsel$FreqMP)
    f2i=max(Minsel$FreqMP)
    Markeri=data.frame(Labeli,t1i,t2i,f1i,f2i)
    if(MaxparFich>Thres){
      MarkersSimplified=rbind(MarkersSimplified,Markeri,use.names=F)
    }
  }
  table(substr(MarkersSimplified$`classe predite`,1,6))
  boxplot(MarkersSimplified$fmin~substr(MarkersSimplified$`classe predite`,1,6),las=2)
  
  names(MarkersSimplified)=c("label","t1","t2","f1","f2")
  #print("L101")
  write.audacity(MarkersSimplified,gsub(".csv",".txt",paste0(dirname(dirname(PredF))
                                                             ,"/marqueurs/G_"
                                                             ,uV2[PositionF1[length(PositionF1)]-1]
                                                             ,"_tdsimplified.txt")))
}
