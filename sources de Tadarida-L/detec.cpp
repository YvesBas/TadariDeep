#include "detec.h"
#include "fenim.h"

using namespace std;

const QString _baseIniFile = "/version.ini";

// Detec class is a thread class which allows the main class to launch
// several parallel threads processing the sound files
Detec::Detec(QMainWindow* parent,int iThread): QThread((QObject *)parent)
{
    _parent=parent;
    PMainWindow= (TadaridaMainWindow *)parent;
    IThread = iThread;
    IDebug = PMainWindow->IDebug;
    _resultSuffix = PMainWindow->ResultSuffix;
    _resultCompressedSuffix = QString("tac");
    MustCancel = false;
    MustCompress = false;
    _collectPreviousVersionsTags = true;
    PDetecTreatment = new DetecTreatment(this);
}

Detec::~Detec()
{
}

// this method is launched by the main class to initialize variables for a treatment
bool Detec::InitializeDetec(const QStringList& wavList, QString soundsPath,bool reprocessingCase,int vl,int vu,bool imadat,bool deepmode,bool withTimeCsv,RematchClass *ro,
                            int modefreq)
{
    _logVersion = vl;
    _userVersion = vu;
    _withTimeCsv = withTimeCsv;
    _fileProblem = false;
    ReprocessingMode = reprocessingCase;
    if(ReprocessingMode) MustCompress = false;
    ImageData = imadat;
    _remObject = ro;
    _modeFreq = modefreq;
    QDate today(QDate::currentDate());
    _wavFileList = wavList;
    _wavPath = soundsPath;
    _txtPath = soundsPath+"/txt";
    QDir reptxt(_txtPath);
    if(!reptxt.exists()) reptxt.mkdir(_txtPath);
    DeepMode = deepmode;
    if(ImageData)
    {
        _datPath = soundsPath+"/dat";
        QDir repdat(_datPath);
        if(!repdat.exists()) repdat.mkdir(_datPath);
        _imagePath = soundsPath+"/ima";
        QDir repima(_imagePath);
        if(!repima.exists()) repima.mkdir(_imagePath);
    }
    if(DeepMode)
    {
        LogStream << "detec : deepmode = true" << endl;
        _ima2Path = soundsPath+"/ima2";
        QDir repima2(_ima2Path);
        if(!repima2.exists()) repima2.mkdir(_ima2Path);
    }
    else
    {
        LogStream << "detec : deepmode = true" << endl;
    }
    _errorFilePath =_txtPath + "/error" + QString::number(IThread+1) + ".log";
    ErrorFile.setFileName(_errorFilePath);
    if(ErrorFile.open(QIODevice::WriteOnly | QIODevice::Text))
    {
    ErrorStream.setDevice(&ErrorFile);
    ErrorFileOpen = true;
    }
    else ErrorFileOpen = false;
    QString logFilePath(_txtPath + "/detec" + QString::number(IThread+1) + ".log");

    _logFile.setFileName(logFilePath);
    _logFile.open(QIODevice::WriteOnly | QIODevice::Text);
    LogStream.setDevice(&_logFile);
	//
    TimeFileOpen = false;
    if(_withTimeCsv)
    {
        QString timePath = _txtPath+ "/time" + QString::number(IThread+1) + ".csv";
        _timeFile.setFileName(timePath);
        if(_timeFile.open(QIODevice::WriteOnly | QIODevice::Text)==true)
        {
            TimeFileOpen = true;
            TimeStream.setDevice(&_timeFile);
            TimeStream.setRealNumberNotation(QTextStream::FixedNotation);
            TimeStream.setRealNumberPrecision(2);
            TimeStream << "filename" << '\t' << "computefft" << '\t' << "noisetreat" << '\t' << "shapesdetects" << '\t' << "parameters" << '\t'
                        << "save - end" << '\t' << "total time(ms)" << endl;
        }
    }
    //
    PDetecTreatment->SetDirParameters(_wavPath,_txtPath,ImageData,_imagePath,_datPath);
    PDetecTreatment->InitializeDetecTreatment();
    //IsRunning = true;
    return(true);
}

// this method handles end treatments when the treatment od Detec object is finished
void Detec::endDetec()
{
    LogStream << "endDetec  IThread = " << IThread << endl;
    if(ReprocessingMode) emit information3(_numberStartTags,_numberEndTags,_numberRecupTags);
    if(_fileProblem) emit dirProblem();
    else writeDirectoryVersion();
    ErrorFile.close();
    if(TimeFileOpen) _timeFile.close();
    if(!ReprocessingMode) emit threadFinished(IThread);
    PDetecTreatment->EndDetecTreatment();
    MustCancel = false;
    if(ReprocessingMode)
    {
        int vdl = _versionDirList.size();
        if(vdl>0) for(int k=0;k<vdl;k++) delete[] _versionIndicators[k];
        delete[] _versionIndicators;
    }
    _logFile.close();
}

// the run() method triggers the processing of the process when the main class executes:
// _pDetec[i] -> start()
// it calls treatOneFile(...) for each file of _wavFileList
void Detec::run()
{
    readDirectoryVersion();
    _nbTreatedFiles = 0;
    _nbErrorFiles = 0;
    for(int i=0;i<NTERRORS;i++) PDetecTreatment->TabErrors[i]=0;
    _filesNumber = _wavFileList.size();
    _fileIndex=0;
    _numberStartTags=0;
    _numberEndTags=0;
    _numberRecupTags=0;
    if(ReprocessingMode && _collectPreviousVersionsTags) createVersionsList();
    //_treating = false;
    for(int i=0;i<_filesNumber;i++)
    {
        if(!treatOneFile())
        {
            LogStream << "treatOneFile = false" << endl;
            break;
        }
    }
    if(ReprocessingMode && _collectPreviousVersionsTags) cleanVerSubdir();
    endDetec();
}

// if a general reprocessing is started, this method prepares variables useful
// for the algorithm of search for labelings of sound events lost in the meantime
void Detec::createVersionsList()
{
    _versionDirList.clear();
    QDir drep(_wavPath);
    QStringList sverList=drep.entryList(QStringList("ver*"), QDir::Dirs);
    int vl,vu,vl2,vu2;
    QStringList lv,lv2;
    QString sv1,sv2;
    bool conv1,conv2;
    foreach(QString sv,sverList)
    {
        lv = sv.right(sv.length()-3).split("_");
        if(lv.size()==2)
        {
            vl=lv.at(0).toInt(&conv1);
            vu=lv.at(1).toInt(&conv2);
            if(conv1 && conv2) _versionDirList.append(sv);
        }
    }
    int vdl =_versionDirList.size();
    if(vdl > 1)
    {
        bool ontrie = true;
        while(ontrie)
        {
            ontrie = false;
            for(int j=0;j<vdl-1;j++)
            {
                sv1 = _versionDirList.at(j);
                sv2 = _versionDirList.at(j+1);
                lv =  sv1.right(sv1.length()-3).split("_");
                lv2 = sv2.right(sv2.length()-3).split("_");
                vl=lv.at(0).toInt(); vu=lv.at(1).toInt();
                vl2=lv2.at(0).toInt(); vu2=lv2.at(1).toInt();
                if(vl>vl2 || (vl==vl2 && vu>vu2))
                {
                    _versionDirList.replace(j,sv2);
                    _versionDirList.replace(j+1,sv1);
                    ontrie=true;
                }
            }
        }

    }
    if(vdl>0)
    {
        _versionIndicators = new int*[vdl];
        for(int k=0;k<vdl;k++)
        {
            _versionIndicators[k] = new int[3];
            for(int l=0;l<3;l++) _versionIndicators[k][l] = 0;
        }
    }

}

// these two methods clean subdirectories of the reference database
// that cannot be useful any more
void Detec::cleanVerSubdir()
{
    QDir wDir(_wavPath);
    if(!wDir.exists()) return;
    for(int j=0;j<_versionDirList.size();j++)
    {
        bool isCleaned = false;
        QString svPath = _wavPath + "/" + _versionDirList.at(j);
        if(j<_versionDirList.size()-1)
        {
            if(_versionIndicators[j][0]==_versionIndicators[j+1][0] && _versionIndicators[j][1]==_versionIndicators[j+1][1]
                    && _versionIndicators[j][2]==_versionIndicators[j+1][2])
            {
                cleanSubdir(wDir,svPath,true,QString("*.*"));
                isCleaned = true;
            }
        } 
        if(!isCleaned)
        {
            cleanSubdir(wDir,svPath+"/txt",true,QString("*.*"));
            cleanSubdir(wDir,svPath+"/ima",true,QString("*.*"));
        }
    } 
    cleanSubdir(wDir,_wavPath+"/dat",false,QString("*.dat"));
    cleanSubdir(wDir,_wavPath+"/txt",false,QString("*.txt"));
    cleanSubdir(wDir,_wavPath+"/txt",false,QString("*.csv"));
    cleanSubdir(wDir,_wavPath+"/txt",false,QString("*.tac"));
}

void Detec::cleanSubdir(QDir cdir,QString ndirPath,bool cleanAll,QString filter)
{
    QDir nDir(ndirPath);
    if(!nDir.exists()) return;
    QStringList listFiles = nDir.entryList(QStringList(filter), QDir::Files);
    foreach(QString f,listFiles) nDir.remove(f);
    if(cleanAll)
    {
        QStringList sdirList = nDir.entryList(QStringList("*"), QDir::Dirs);
        foreach(QString r,sdirList)
        {
            if(r.length()>2)
            {
                cleanSubdir(nDir,ndirPath+"/"+r,true,"*.*"); // attention : récursivité
            }
        }
        cdir.rmdir(ndirPath);
    }
}

// this method manages the treatments for one file
// after initializations, it calls : PDetecTreatment::CallTreatmentsForOneFile
// which handles computings
// in reprocessing mode, it processes also the informations related to this reprocessing
bool Detec::treatOneFile()
{
    if((MustCancel  && !ReprocessingMode) || _fileProblem) return(false);
    QString wavFile = _wavFileList.at(_fileIndex);
    _wavFile = wavFile;
    _fileIndex++;
    LogStream << endl;
    LogStream << endl << "tOF : "<< QDateTime::currentDateTime().toString("hh:mm:ss:zzz") << endl;
    LogStream << "wavfile=" << wavFile << endl;
    QString nomfic = wavFile;
    if(ReprocessingMode)
    {
        _remObject->initialize();
        _numberStartTags+=_remObject->PreMatch(wavFile,_wavPath);
        NumVer = _remObject->Fenim1->NumVer;
        TE = _remObject->Fenim1->PtE;
        NumtE = _remObject->Fenim1->NumtE;
    }
    //
    emit information(nomfic);
    QString pathFile = _wavPath + '/' + wavFile;
    if(checkAssociatedFiles(_wavPath,_wavFile)== false)
    {
        if(ErrorFileOpen) ErrorStream << _wavFile << ": associated file problem" << endl;
		
        _fileProblem = true;
        return(false);
    }
    if(PDetecTreatment->CallTreatmentsForOneFile(wavFile,pathFile))
	{
        if(ImageData)
        {
            createImage(wavFile);
            saveDatFile(wavFile);
        }
        if(DeepMode)
        {
            int nbcris = (int)PDetecTreatment->CallsArray.size();
            for (int i = 0 ; i < nbcris ; i++)
            {
                createDeepImage(wavFile,i);
            }
        }
        _nbTreatedFiles++;
	}
    else
    {
        _nbErrorFiles++;
        if(PDetecTreatment->NError >=0 && PDetecTreatment->NError<NTERRORS) PDetecTreatment->TabErrors[PDetecTreatment->NError]++;
    }
    // -------------------------------------------------------
    if(ReprocessingMode)
    {
        int pcpma;
        int nbTags = _remObject->PostMatch(true,"",&pcpma);
        if(_remObject->Ok)
        {
            _numberEndTags+=nbTags;
            QString info0=wavFile+QString(" : ")
                    + QString::number(_remObject->Nbc2)+QString(" cries out of ")
                    + QString::number(_remObject->Nbc1)+".";
            QString info1=wavFile+QString(" : ")
                    + QString::number(nbTags)+QString(" labels matched out of ")
                    + QString::number(_remObject->Nbe1)+".";
            QString info2=_wavPath+QString(" : ")
                    + QString::number(_numberEndTags)+QString(" labels matched out of ")
                    + QString::number(_numberStartTags)+".";

            LogStream << info2 << endl;
            if(_fileIndex == _filesNumber)
            {
                emit information2b(info2,true);
                LogStream << "Folder matching "<< info2 << endl;

            }
            emit information2b(info2,false);
            // recovery loop from previous versions
            if(_collectPreviousVersionsTags)
            {
                for(int j=_versionDirList.size()-1;j>=0;j--)
                {
                    QString verPath = _wavPath + "/" + _versionDirList.at(j);
                    _remObject->PreMatch(wavFile,verPath);
                    _versionIndicators[j][0] += _remObject->Nbc1;
                    _versionIndicators[j][1] += _remObject->Nbe1;
                    _remObject->PostMatch(false,verPath,_versionIndicators[j]+2);
                    if(_remObject->Nbe2 > 0)
                    {
                        _numberRecupTags += _remObject->Nbe2;
                        nbTags += _remObject->Nbe2;
                        info1=wavFile+QString(" - after recovering out of version ")
                          +verPath+" : "+QString::number(nbTags)+QString(" matched labels.");
                        LogStream << info1 << endl;
                        info2=_wavPath + QString(" : ") + QString::number(_numberEndTags+_numberRecupTags)
                                + QString(" matched labels.");
                        emit information2b(info2,true);
                        LogStream << info2 << endl;
                    }
                }
            }
            _remObject->EndMatch();
        }
    }
    emit information4(IThread,_nbTreatedFiles,_nbErrorFiles);
    _sleep(10);
    LogStream << "end of file treatment" << endl;
    //emit moveBar((float)_fileIndex/(float)_filesNumber);
    //_treating = false;
    return(true);
}

// this method reads version of a treated directory in version.ini
bool Detec::readDirectoryVersion()
{
    QString cbase = _wavPath + _baseIniFile;
    _dirLogVersion = 0;
    _dirUserVersion = 0;
    _dirModeFreq = 0;
    if(!QFile::exists(cbase)) return(false);
    QSettings settings(cbase, QSettings::IniFormat);
    settings.beginGroup("version");
    _dirLogVersion = settings.value("log").toInt();
    _dirUserVersion = settings.value("user").toInt();
    _dirModeFreq = settings.value("modeFreq").toInt();
    if(_dirLogVersion < 22 && _dirModeFreq == 0) _dirModeFreq = 1;
    settings.endGroup();
    return(true);
}

// this method writes version of a treated directory in version.ini
void Detec::writeDirectoryVersion()
{
    QSettings settings(_wavPath + _baseIniFile, QSettings::IniFormat);
    settings.beginGroup("version");
    settings.setValue("log", QVariant::fromValue(_logVersion));
    settings.setValue("user", QVariant::fromValue(_userVersion));
    settings.setValue("modeFreq", QVariant::fromValue(_modeFreq));
    settings.endGroup();
}


// this method checks output files which must be associated with a treated wav file
bool Detec::checkAssociatedFiles(QString pathName,QString wavName)
{
    bool resu = true;
    QString shortName;
    QString testName;
    if(wavName.length()>4) shortName = wavName.left(wavName.length()-4);
    else return(false);
    for(int i=0;i<4;i++)
    {
        if(i==0) testName = pathName + "/txt/" + shortName + "." + _resultSuffix;
        if(i==1) testName = pathName + "/eti/" + shortName + ".eti";
        if(i==2) testName = pathName + "/da2/" + shortName + ".da2";
        if(i==3) testName = pathName + "/ima/" + shortName + ".jpg";
        QFile testFile;
        testFile.setFileName(testName);
        if(testFile.exists())
        {
            if(testFile.open(QIODevice::WriteOnly))
            {
                testFile.close();
            }
            else
            {
                LogStream << testName << " : file opening problem" << endl;
                resu = false;
                break;
            }
        }
    }
    //
    return(resu);
}

// this method creates the pciture which will be used to watch sound events and/or
// to enter labels for them
void Detec::createImage(QString wavFile)
{
    if(PDetecTreatment->SonogramWidth > 32767) {_xHalf = true; _imaWidth=(PDetecTreatment->SonogramWidth+1)/2;}
    else  {_xHalf = false; _imaWidth=PDetecTreatment->SonogramWidth;}
    int lyi = qMin(PDetecTreatment->FftHeightHalf,PDetecTreatment->LimY);
    QImage ima = QImage(_imaWidth, lyi,QImage::Format_RGB32);
    initBvrvb(PDetecTreatment->EnergyMin,PDetecTreatment->EnergyMax);
    int imax=((int)(PDetecTreatment->EnergyMax-PDetecTreatment->EnergyMin)*5)+1;
    uint crgb;
    for(int i=0;i<imax;i++)
    {
        _tvaleur[i]=calculateRGB((double)i/5.0f);
    }
    qint16 *ydl;
    int exceptions = 0;
    int blanc = qRgb(250,250,250);
    int noir = qRgb(5,5,5);
    int grisclair = qRgb(230,230,230);
    int grisfonce = qRgb(25,25,25);
    LogStream << "lyi=" << lyi << endl;
    for(int y = 0; y < lyi ; y++)
    {
        if(y<6 && PDetecTreatment->WithSilence)
        {
            int xr = 0;
            for (int x = 0 ; x < _imaWidth ; x++)
            {
                crgb=0;
                if(y<3)
                {
                    if(PDetecTreatment->FlagGoodColInitial[xr]==true) crgb = grisclair; else crgb = grisfonce;
                 }
                else
                {
                    if(PDetecTreatment->FlagGoodCol[xr]==true) crgb = blanc; else crgb = noir;
                }
                ima.setPixel(x, lyi-y-1,crgb);
                xr+=1+_xHalf;
            }
        }
        else
        {
            ydl=PDetecTreatment->SonogramArray[y];
            int digitPos = 0;
            char *pBoolChar = PDetecTreatment->PointFlagsArray[y];;
            char boolChar = *pBoolChar;
            for (int x = 0 ; x < _imaWidth ; x++)
            {
                int valeur=(int)(((float)(*ydl)/20.0f)  -  PDetecTreatment->EnergyMin*5.0f);
                if(valeur>=0 && valeur<imax)crgb=_tvaleur[valeur];
                else {crgb=0; exceptions++;}
                //if((boolChar & (1 << digitPos))!=0) crgb |= 224 << 16;
                ima.setPixel(x, lyi-y-1,crgb);
                for(int k=0;k<1+_xHalf;k++)
                {
                    ydl++;
                    digitPos++;
                    if(digitPos==8) {pBoolChar++; boolChar = *pBoolChar; digitPos=0;}
                }
            }
        }
    }
    _imageFullName = _imagePath + '/' + wavFile.replace(QString(".wav"), QString(".jpg"), Qt::CaseInsensitive);
    ima.save(_imageFullName,0,100); // save image
}

// this method sets parameters determining the colors of the image
// highlighting the cries, the peaks of energy ...
void Detec::initBvrvb(double bornemin,double bornemax)
{
    _bRGB[0][0]=bornemin;
    _bRGB[1][0]=bornemin/2;
    _bRGB[2][0]=(double)PDetecTreatment->EnergyStopThreshold;
    _bRGB[3][0]=(double)PDetecTreatment->EnergyShapeThreshold;
    _bRGB[4][0]=bornemax+1;
    for(int i=0;i<5;i++) _bRGB[i][0]-=bornemin;
    _bRGB[0][1]=0;   _bRGB[0][2]=0;   _bRGB[0][3]=0;
    _bRGB[0][4]=0;   _bRGB[0][5]=0;   _bRGB[0][6]=32;

    _bRGB[1][1]=0;   _bRGB[1][2]=0;  _bRGB[1][3]=32;
    _bRGB[1][4]=0;   _bRGB[1][5]=0;  _bRGB[1][6]=64;

    _bRGB[2][1]=48;   _bRGB[2][2]=0; _bRGB[2][3]=80;
    _bRGB[2][4]=140;   _bRGB[2][5]=0; _bRGB[2][6]=92;

    _bRGB[3][1]=160;  _bRGB[3][2]=0;  _bRGB[3][3]=96;
    _bRGB[3][4]=255;  _bRGB[3][2]=0;  _bRGB[3][3]=192;
}

// this method sets the color of a pixel according to a pair of time/frequency values
// and its sound energy level
uint Detec::calculateRGB(double value)
{
    double rgb[3];
    for(int j=0;j<3;j++) rgb[j] =0.0f;
    for(int i=0;i<4;i++)
    {
        if(value>=_bRGB[i][0] && value<_bRGB[i+1][0])
        {
            for(int j=0;j<3;j++)
                rgb[j]=_bRGB[i][j+1]
                        +((_bRGB[i][j+4]-_bRGB[i][j+1])*(value-_bRGB[i][0]))/(_bRGB[i+1][0]-_bRGB[i][0]);
            break;
        }
    }
    uint urgb = qRgb(qRound(rgb[0]),qRound(rgb[1]),qRound(rgb[2]));
    return(urgb);
}

// this method saves a .da2 file after treatment, it saves all the informations
// which will be useful to show and/or treat a sound event
void Detec::saveDatFile(QString wavFile)
{
    QString da2file = wavFile.replace(QString(".wav"),QString(".da2"), Qt::CaseInsensitive);
    _callMatrixName = _datPath + '/' + da2file;
    _callMatrixFile.setFileName(_callMatrixName);
    _callMatrixFile.open(QIODevice::WriteOnly);
    _callMatrixStream.setDevice(&_callMatrixFile);
    _callMatrixStream << _logVersion;
    _callMatrixStream << _userVersion;

    int nbcris = (int)PDetecTreatment->CallsArray.size();
    _callMatrixStream << nbcris;
    _imageHeight = qMin(PDetecTreatment->FftHeightHalf,PDetecTreatment->LimY);
    _callMatrixStream << _imageHeight;
    _callMatrixStream << (int)_xHalf;
    _callMatrixStream << (float)(PDetecTreatment->MsPerX);
    _callMatrixStream << (float)(PDetecTreatment->KhzPerY);
    _callMatrixStream << (int)(PDetecTreatment->TimeExpansion);

    LogStream << "savedatfile : " << endl;
    LogStream << "   FftHeightHalf=" << QString::number(PDetecTreatment->FftHeightHalf) << endl;
    LogStream << "   lyi=" << QString::number(_imageHeight) << endl;
    LogStream << "   _xHalf=" << QString::number(_xHalf) << endl;
    LogStream << "   MsPerX=" << QString::number(PDetecTreatment->MsPerX) << endl;
    LogStream << "   KhzPerY=" << QString::number(PDetecTreatment->KhzPerY) << endl;

    for(int i=0;i<nbcris;i++)
    {
        _callMatrixStream <<PDetecTreatment-> MasterPoints[i].x();
        _callMatrixStream << PDetecTreatment->MasterPoints[i].y();
        int nbPixel=PDetecTreatment->CallsArray[i].size();
        _callMatrixStream << nbPixel;
        int x,y;
        float e;
        for(int j=0;j<nbPixel;j++)
        {
            x = PDetecTreatment->CallsArray[i].at(j).x();
            y = PDetecTreatment->CallsArray[i].at(j).y();
            e = (float)PDetecTreatment->SonogramArray[y][x]/100.0f;
            _callMatrixStream << x;
            _callMatrixStream << y;
            _callMatrixStream << e;
        }
        int longCri=PDetecTreatment->CallMasterRidgeArray[i].size();
        _callMatrixStream << longCri;
        for(int j=0;j<longCri;j++)
        {
            _callMatrixStream << PDetecTreatment->CallMasterRidgeArray[i][j].x();
            _callMatrixStream << PDetecTreatment->CallMasterRidgeArray[i][j].y();
        }
        longCri=PDetecTreatment->CallSouthArray[i].size();
        _callMatrixStream << longCri;
        for(int j=0;j<longCri;j++)
        {
            _callMatrixStream << PDetecTreatment->CallSouthArray[i][j].x();
            _callMatrixStream << PDetecTreatment->CallSouthArray[i][j].y();
        }
        longCri=PDetecTreatment->CallNorthRidgeArray[i].size();
        _callMatrixStream << longCri;
        for(int j=0;j<longCri;j++)
        {
            _callMatrixStream << PDetecTreatment->CallNorthRidgeArray[i][j].x();
            _callMatrixStream << PDetecTreatment->CallNorthRidgeArray[i][j].y();
        }
        longCri=PDetecTreatment->CallWestRidgeArray[i].size();
        _callMatrixStream << longCri;
        for(int j=0;j<longCri;j++)
        {
            _callMatrixStream << PDetecTreatment->CallWestRidgeArray[i][j].x();
            _callMatrixStream << PDetecTreatment->CallWestRidgeArray[i][j].y();
        }
        longCri=PDetecTreatment->CallSecondWestRidgeArray[i].size();
        _callMatrixStream << longCri;
        for(int j=0;j<longCri;j++)
        {
            _callMatrixStream << PDetecTreatment->CallSecondWestRidgeArray[i][j].x();
            _callMatrixStream << PDetecTreatment->CallSecondWestRidgeArray[i][j].y();
        }
        for(int jcrete=0;jcrete<NCRETES;jcrete++)
        {
           _callMatrixStream << PDetecTreatment->LowSlope[(i*NCRETES+jcrete)*2] << PDetecTreatment->LowSlope[(i*NCRETES+jcrete)*2+1];
           _callMatrixStream << PDetecTreatment->Inflexion1[(i*NCRETES+jcrete)*2]  << PDetecTreatment->Inflexion1[(i*NCRETES+jcrete)*2+1];
           _callMatrixStream << PDetecTreatment->Inflexion3[(i*NCRETES+jcrete)*2]   << PDetecTreatment->Inflexion3[(i*NCRETES+jcrete)*2+1];
        }
    } 
    _callMatrixStream << PDetecTreatment->SonogramWidth;
    _callMatrixStream << (int)(PDetecTreatment->WithSilence);
    if(PDetecTreatment->WithSilence)
    {
        for(int j=0;j<PDetecTreatment->SonogramWidth;j++)
        {
            _callMatrixStream << (qint8)(PDetecTreatment->FlagGoodCol[j]) << (qint8)(PDetecTreatment->FlagGoodColInitial[j]) << (qint8)(PDetecTreatment->EnergyColumAverage[j]);
        }
    }

    // -------------------
    _callMatrixFile.close();
}
// --------------------------------------------------------------------------------------
// $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
// --------------------------------------------------------------------------------------
bool Detec::createDeepImage(QString wavFile,int callNumber)
{
    bool xHalf;
    int imaWidth;
    LogStream << "dcdi debut - callnumber=" << callNumber << endl;
    if(PDetecTreatment->SonogramWidth > 32767) {xHalf = true; imaWidth=(PDetecTreatment->SonogramWidth+1)/2;}
    else  {xHalf = false; imaWidth=PDetecTreatment->SonogramWidth;}
    int lyi = _imageHeight;
    if(lyi != 128)
    {
        LogStream << "hauteur image # 128 : non gere pour l'instant !" << endl;
        return(false);
    }
    //
    QPoint p =PDetecTreatment-> MasterPoints[callNumber];
    int xmp = p.x(),ymp = p.y();
    float eCall = (float)PDetecTreatment->SonogramArray[ymp][xmp]/100.0f;
    int MpIn = (int)(eCall*100.0d);
    int MpHz = (int)((double)(PDetecTreatment->_paramsArray[callNumber][0][FreqMP]*1000.0d));
    int MpMs = (int)((double)(PDetecTreatment->_paramsArray[callNumber][0][StTime]));
    int MDur = (int)((double)(PDetecTreatment->_paramsArray[callNumber][0][Dur]));
    if(MDur < 9)
    {
        LogStream << "duree trop courte - image ima2 non enregistree !" << endl;
        return(false);
    }
    if(MpHz < 500 || MpHz > 10000)
    {
        LogStream << "frequence du point maitre hors limites ! MpHz=" << MpHz << endl;
        return(false);
    }


    //
    QImage ima = QImage(imaWidth, lyi,QImage::Format_RGB32);
    // $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    // chargement de l'image precedemment cr??e pour ne pas recr?er tout et parce que dans le fichier .dat
    // on n'a pas toute l'information de SonogramArray mais seulement celle des cris
    ima.load(_imageFullName); // save image
    // $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    // mise en valeur du cri
    int ycrimax = 0;
    int ycrimin = lyi;
    int xmin=6128,xmax=0;

    QVector<QPoint> unemat = PDetecTreatment->CallsArray[callNumber];

    for(int j=0;j<unemat.size();j++)
    {
        int xr = unemat.at(j).x();
        int yr = unemat.at(j).y();
        if(yr > ycrimax) ycrimax = yr;
        if(yr < ycrimin) ycrimin = yr;
        if(xr > xmax) xmax = xr;
        if(xr < xmin) xmin = xr;

        //int ener = EnergyMatrix[callNumber][j];
        QRgb rgb = ima.pixel(xr,lyi-yr-1);
        int newRed = qRed(rgb);
        newRed = (int)((qRed(rgb) + 255)/2);
        //int newGreen = (int)((qGreen(rgb) + 255)/2);
        // int newGreen = (int)(((lyi-yr)*255)/lyi);
        int newGreen = (int)(((lyi-yr)*255)/lyi);
        //int newBlue = (int)( (qBlue(rgb) + 255) / 2 );
        //int newBlue = (int) qBlue(rgb);
        int newBlue = (int) ((qBlue(rgb)*3+255)/4);
        ima.setPixel(xr,lyi-yr-1,(uint)(qRgb(newRed,newGreen,newBlue)));
    }
    // $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    // mise en valeur du cri
    // mise en valeur du point maitre et des cretes
//
    LogStream << "dcdi milieu" << callNumber << endl;

    //----
    // cretes :

    for(int jcrete=0;jcrete<3;jcrete++)
    {
        QVector<QPoint> crestMat;
        if(jcrete==0) crestMat = PDetecTreatment->CallMasterRidgeArray[callNumber];
        if(jcrete==1) crestMat = PDetecTreatment->CallSouthArray[callNumber];
        if(jcrete==2) crestMat = PDetecTreatment->CallNorthRidgeArray[callNumber];
        int ng = 80;
        if(jcrete==0) ng = 32;
        for(int j=0;j<crestMat.size();j++)
        {

            int x=(int)(crestMat[j].x()/(1+xHalf));
            int y=(int)(lyi-crestMat[j].y()-1);
            if(jcrete==1 && y>0) y++;
            if(jcrete==2 && y<lyi-1) y--;
            //if(jcrete!=3) x+=0.5f; else x+=0.05f;
            //if(jcrete==1) y+=1;
            ima.setPixel(x,y,(uint)(qRgb(ng,ng,ng)));
        }
        //
    } // next jcrete
    //---
    // point maitre
    if(xmp > 0 && xmp < imaWidth-1 && ymp > 0 && ymp < lyi-1)
    {
        ima.setPixel(xmp-1,lyi-ymp-2,(uint)(qRgb(0,0,0)));
        ima.setPixel(xmp,lyi-ymp-2,(uint)(qRgb(0,0,0)));
        ima.setPixel(xmp+1,lyi-ymp-2,(uint)(qRgb(0,0,0)));
        ima.setPixel(xmp-1,lyi-ymp-1,(uint)(qRgb(0,0,0)));
        ima.setPixel(xmp+1,lyi-ymp-1,(uint)(qRgb(0,0,0)));
        ima.setPixel(xmp-1,lyi-ymp,(uint)(qRgb(0,0,0)));
        ima.setPixel(xmp,lyi-ymp,(uint)(qRgb(0,0,0)));
        ima.setPixel(xmp+1,lyi-ymp,(uint)(qRgb(0,0,0)));
    }
    ima.setPixel(xmp,lyi-ymp-1,(uint)(qRgb(255,255,255)));
    // $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    // modification des autres cris
    for(int i=0;i<PDetecTreatment->_callsNumber;i++)
    {
        if(i!= callNumber)
        {
            int ympc = PDetecTreatment->MasterPoints[i].y();
            int xmpc = PDetecTreatment->MasterPoints[i].x();
            bool afavoriser = false;
            if(ympc > ycrimin && ympc < ycrimax) afavoriser = true;
            QVector<QPoint> unemat = PDetecTreatment->CallsArray[i];
            for(int j=0;j<unemat.size();j++)
            {
                int xr = unemat.at(j).x();
                int yr = unemat.at(j).y();
                //int ener = EnergyMatrix[callNumber][j];
                QRgb rgb = ima.pixel(xr,lyi-yr-1);
                int newRed = (int)(qRed(rgb)/5);
                if(afavoriser) newRed = (int)(qRed(rgb)/2);
                //int newGreen = (int)((qGreen(rgb) + 255)/2);
                int newGreen = (int)(((lyi-yr)*255)/(lyi*5));
                if(afavoriser) newGreen = (int)(((lyi-yr)*255)/(lyi*2));
                //int newBlue = (int)((qBlue(rgb) + 255)/2);
                int newBlue = (int) ( (qBlue(rgb)*2) / 3);
                if(afavoriser) newBlue = (int) ((qBlue(rgb)+255)/2);
                ima.setPixel(xr,lyi-yr-1,(uint)(qRgb(newRed,newGreen,newBlue)));
            }
            // ajouter aussi petite coloration du masterpoint
            ima.setPixel(xmpc,lyi-ympc-1,(uint)(qRgb(32,32,32)));

        }
    }
    // $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    int dlarp = 500;
    int xcd = xmp - dlarp;
    if(xcd < 0) xcd = 0;
    int xcf = xmp + dlarp - 1;
    if(xcf > imaWidth - 1) xcf = imaWidth - 1;
    //
    QString EndName = QString("--") + QString::number(callNumber)
            + QString("--") + QString::number(MpIn)
            + QString("--") + QString::number(MDur)
            + QString("--") + QString::number(MpHz)
            + QString("--") + QString::number(MpMs)
            + ".jpg";
    QString wavRadic = wavFile.replace(".wav","");
    QString callIma2Name = _ima2Path + "/" + wavRadic + EndName;

    if(xmp > imaWidth-5 || xmp <5)
    {
        LogStream << callIma2Name << " : point maitre trop pres des bords" << endl;
        return(false);
    }
    LogStream << "dcdi proche fin" << callNumber << endl;

    QImage imac = ima.copy(xcd,0,xcf-xcd+1,lyi);

    // calcul de endname : a gerer dans une autre methode  :
    LogStream << "callIma2Name=" << callIma2Name << endl;
    imac.save(callIma2Name,0,100); // save image
    return(true);
}
