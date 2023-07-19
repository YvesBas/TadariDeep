DirIn="D:/PSI-BIOM/Travail/Enregistrements opportunistes"
DirOut="E:/PSIBIOM/Enregistrementsopportunistes"


Files=list.files(DirIn,recursive=T,full.names=T)

table(substr(Files,nchar(Files)-3,nchar(Files)))

FilesW=subset(Files,grepl(".wav",Files,ignore.case=T))
FilesT=subset(Files,grepl(".txt",Files,ignore.case=T))
FilesW=subset(FilesW,!grepl("/Fichiers bruts/",FilesW))

test=match(basename(FilesW),basename(FilesW))
plot(test)
Comp=c(1:length(test))
plot(test-Comp)
PbTest=subset(FilesW,test-Comp<0)

test=match(basename(FilesT),basename(FilesT))
plot(test)
Comp=c(1:length(test))
plot(test-Comp)
PbTest=subset(FilesT,test-Comp<0)
PbTest=subset(PbTest,!grepl("Summary.txt",PbTest))
PbTest=subset(PbTest,!grepl("log.txt",PbTest))

FilesWT=c(FilesW,FilesT)

NewName=paste0(DirOut,"/",basename(FilesWT))

testC=file.copy(from=FilesWT,to=NewName)
summary(testC)
