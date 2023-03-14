library(data.table)

DirBN="C:/Users/yvesb/Downloads/GSampleV3_Part1/bnauda_p1_auda"
#DirBN="C:/Users/yvesb/Downloads/GSampleV3part2/bnauda_auda"
Dir="C:/Users/yvesb/Downloads/GSampleV3_Part1/PA_230102"
#Dir="C:/Users/yvesb/Downloads/GSampleV3part2/PA_230102"
DirW="C:/Users/yvesb/Downloads/GSampleV3_Part1"
#DirW="C:/Users/yvesb/Downloads/GSampleV3part2"
#TableSpeciesSel=fread("species_2022-12-01_sel.csv")
TableSpeciesSel=NA
FilterPeriod="Dawn"
FilterOutConf=T
DataPeriod=fread("C:/Users/yvesb/Documents/Tadarida/Vigie-Chiro_scripts/Vigie-Chiro_scripts/SummaryPeriod.csv")
DataConf=fread("C:/Users/yvesb/Documents/Tadarida/Vigie-Chiro_scripts/Vigie-Chiro_scripts/SummaryConfidential.csv")
DirOut="C:/Users/yvesb/Downloads/GSampleV3_Part1/PourElodie230102"

dir.create(DirOut)


Files=list.files(Dir,full.names=T)
#,pattern="tdauda")
Sub=substr(basename(Files),1,24)

if(FilterOutConf){
  ListOpen=subset(DataConf$ListCarre,DataConf$Conf==0)
  ListOpen=subset(ListOpen,ListOpen!="")
  ListOpen=subset(ListOpen,!grepl("irods",ListOpen))
  FilesFiltered=vector()
  for (h in 1:length(ListOpen)){
    Fileh=subset(Files,grepl(paste0("Car",ListOpen[h]),basename(Files)))
    FilesFiltered=c(FilesFiltered,Fileh)
  }
FilesFU=unique(FilesFiltered)  
Files=FilesFU
}

if(!is.na(FilterPeriod)){
  ListPeriod=subset(DataPeriod$ListPref,DataPeriod$Nocturnal==FilterPeriod)
  FilesFiltered=vector()
  for (h in 1:length(ListPeriod)){
    Fileh=subset(Files,grepl(ListPeriod[h],basename(Files)))
    FilesFiltered=c(FilesFiltered,Fileh)
  }
  FilesFU=unique(FilesFiltered)  
  Files=FilesFU
}

Dest1=gsub(Dir,DirOut,Files)
file.copy(from=Files,to=Dest1)

Pref=gsub("_tdauda.txt","",basename(Files))

AllBN=list.files(DirBN,full.names=T)
AllW=list.files(DirW,full.names=T,pattern=".wav$")


FilesBN=vector()
FilesW=vector()
for (j in 1:length(Pref)){
    BNj=subset(AllBN,grepl(Pref[j],basename(AllBN)))
FilesBN=c(FilesBN,BNj)
Wj=subset(AllW,grepl(Pref[j],basename(AllW)))
FilesW=c(FilesW,Wj)
}


Dest2=gsub(DirBN,DirOut,FilesBN)
file.copy(from=FilesBN,to=Dest2)

Dest3=gsub(DirW,DirOut,FilesW)
file.copy(from=FilesW,to=Dest3)
