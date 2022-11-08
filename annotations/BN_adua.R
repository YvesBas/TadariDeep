library(data.table)
BNinitDir="C:/Users/yvesb/Documents/Tadarida/Dbas_deepL/SampleV3/bnauda_p1"


BNnew=paste0(BNinitDir,"_auda")

dir.create(BNnew)


Files=list.files(BNinitDir,full.names=T)


datalist=list()
for (i in 1:length(Files)){
  test=fread(Files[i])
  if(nrow(test)>0){
SpInfo=tstrsplit(test$V3,split=" ")
SpCode=paste0(substr(SpInfo[[1]],1,3),substr(SpInfo[[2]],1,4))
    table(SpCode)
    Confiance=round(test$V4*100)
    test$V3=paste(SpCode,"-",Confiance)
    fwrite(test,paste0(BNnew,"/",basename(Files[i])),sep="\t")    
    datalist[[i]]=test
    
    datalist[[i]]$file=basename(Files[i])
  }
}
dataAll=rbindlist(datalist)

table(substr(dataAll$V3,1,7))[order(table(substr(dataAll$V3,1,7))
                                    ,decreasing = T)]
