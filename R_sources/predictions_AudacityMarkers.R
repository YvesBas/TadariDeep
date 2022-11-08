FilePredictions=file.choose()

PredictionAll=read.csv2(FilePredictions)

MarkerDir=paste0(dirname(FilePredictions),"/markers")

dir.create(MarkerDir)

ListWaves=unique(PredictionAll$fichier.wav)

for (i in 1:length(ListWaves)){
  
  Predictions=subset(PredictionAll,PredictionAll$fichier.wav==ListWaves[i])
  
  CallInfos=tstrsplit(Predictions$fichier.jpg,split="--")
  
  LCI=length(CallInfos)
  
  V1=as.numeric(gsub(".jpg","",CallInfos[[LCI]]))/1000
  hist(V1)
  Duration=as.numeric(CallInfos[[LCI-2]])
  hist(Duration)
  V2=V1+Duration/1000
  
  V3=paste(Predictions$classe.predite,round(as.numeric(Predictions$pourcentage.prediction)),"-",CallInfos[[LCI-1]],"Hz")
  print(head(V3))
  marker=data.frame(V1,V2,V3)
  #write.table(marker,gsub(".csv","_ForAudacity.csv",FilePredictions),col.names=F,row.names=F)
  write.table(marker,paste0(MarkerDir,"/",ListWaves[i],"_ForAudacity.txt"),col.names=F,row.names=F,sep="\t")
  
}
