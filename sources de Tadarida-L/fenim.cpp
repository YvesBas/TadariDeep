#include "etiquette.h"
#include "loupe.h"
#include "fenim.h"
#include "detectreatment.h"

const QString _baseIniFile = "/version.ini";

// Fenim.cpp contains the code for two "associated" classes
// Fenim class handles the treatments used to show the picture corresponding to
// a treated file and allows an expert user to enter labels for its sound events...
// fenim class doesn't contain graphical objects

// FenimWindow object is created by CreatFenimWindow method of Fenim class
// which is called by ShowFenim method of Fenim class
// which is called by showPicture method of main class (TadaridaMainWindow)
// in both cases of labelling or updating labellings
// (the two treatments proposed by the interface)
// FenimWindow object contains graphical objects of IHM

// Fenim objects can also be used without FenimWindow objects in order to use
// methods useful for general reprocessing

FenimWindow::FenimWindow(Fenim *pf,QMainWindow *parent) : QMainWindow(parent)
{
    PFenim = pf;
    _alreadyScaled = false;
    _countResize = 0;
    GBoxInput = new QGroupBox(this);
}

// these are methods triggered by HMI events of then FenimWindow class
// which launch methods of processing belonging to the Fenim class
void FenimWindow::ValidateLabel() { PFenim->ValidateLabel(); }
void FenimWindow::SaveLabels() { PFenim->SaveLabels(); }
void FenimWindow::CloseFenim() { PFenim->CloseFenim(); }
void FenimWindow::NextCall() { PFenim->NextCall(); }
void FenimWindow::PreviousCall() { PFenim->PreviousCall(); }
void FenimWindow::EndCall() { PFenim->EndCall(); }
void FenimWindow::StartCall() { PFenim->StartCall(); }
void FenimWindow::SelectIndex(int a) { PFenim->SelectIndex(a); }
void FenimWindow::UpdateIndex(const QString& s) { PFenim->UpdateIndex(s); }
void FenimWindow::ClickConfi() { PFenim->ClickConfi(); }
void FenimWindow::Zoom() { PFenim->Zoom(); }
void FenimWindow::UnZoom() { PFenim->UnZoom(); }
void FenimWindow::ActivateGrid(int a) { PFenim->ActivateGrid(a); }
void FenimWindow::ActivateMasterPoints() { PFenim->ActivateMasterPoints(); }
void FenimWindow::ActivateCrests() { PFenim->ActivateCrests(); }
void FenimWindow::SelectEditedCalls() { PFenim->SelectEditedCalls(); }
void FenimWindow::SelectSpecTags(const QString& codsel) { PFenim->SelectSpecTags(codsel); }
void FenimWindow::SpecTagNext() { PFenim->SpecTagNext(); }
void FenimWindow::SpecTagPrevious() { PFenim->SpecTagPrevious(); }
void FenimWindow::SpecTagLast() { PFenim->SpecTagLast(); }
void FenimWindow::SpecTagFirst() { PFenim->SpecTagFirst(); }

// this method connects the signals (event handlers) to methods
void FenimWindow::CreateConnections()
{
    connect(BClose,SIGNAL(clicked()),this,SLOT(close()));
    connect(BRightArrow,SIGNAL(clicked()),this,SLOT(NextCall()));
    connect(BLeftArrow,SIGNAL(clicked()),this,SLOT(PreviousCall()));
    connect(BEndArrow,SIGNAL(clicked()),this,SLOT(EndCall()));
    connect(BStartArrow,SIGNAL(clicked()),this,SLOT(StartCall()));
    connect(BSaveOneLabel,SIGNAL(clicked()),this,SLOT(ValidateLabel()));
    connect(BSaveLabels,  SIGNAL(clicked()),this,SLOT(SaveLabels()));
    connect(PFenim->PFC[INDICE]->SLid, SIGNAL(valueChanged(int)), this, SLOT(SelectIndex(int)));
    connect(PFenim->PFC[INDICE]->LE,SIGNAL(textEdited(const QString&)),this,SLOT(UpdateIndex(const QString&)));
    connect(PFenim->PFC[CONFIDENTIEL]->ChB, SIGNAL(stateChanged(int)), this, SLOT(ClickConfi()));
    connect(BZoom,SIGNAL(clicked()),this,SLOT(Zoom()));
    connect(BUnZoom,SIGNAL(clicked()),this,SLOT(UnZoom()));
    connect(BCGrid,SIGNAL(stateChanged(int)),this,SLOT(ActivateGrid(int)));
    connect(BCMasterPoints,SIGNAL(stateChanged(int)),this,SLOT(ActivateMasterPoints()));
    connect(BCCalls,SIGNAL(stateChanged(int)),this,SLOT(ActivateCrests()));
    connect(EditCall,SIGNAL(editingFinished()),this,SLOT(SelectEditedCalls()));
    connect(ChbTagSpec,SIGNAL(activated(const QString&)), this, SLOT(SelectSpecTags(const QString&)));
    connect(BRightArrowSpec,SIGNAL(clicked()),this,SLOT(SpecTagNext()));
    connect(BLeftArrowSpec,SIGNAL(clicked()),this,SLOT(SpecTagPrevious()));
    connect(BEndArrowSpec,SIGNAL(clicked()),this,SLOT(SpecTagLast()));
    connect(BStartArrowSpec,SIGNAL(clicked()),this,SLOT(SpecTagFirst()));
}

// FieldClass : this class is used to set the input objects of the window
FieldClass::FieldClass(QWidget *parent,Fenim *pf,QString title,int fieldType,bool obl,bool unic,QString fieldCode,bool allowAdd,int smin,int smax,QString englishLabel)
{
  PFenim = pf;
  FieldType = fieldType;
  Obl = obl;
  Unic = unic;
  Title = title;
  FieldCode = fieldCode;
  EnglishLabel = englishLabel;
  TitleLabel = new MyQLabel(parent);
  TitleLabel->SetText(title);
  EnglishLabel = englishLabel;
  if(FieldType==EC)
  {
      ECo = new EditCombo(parent,pf,FieldCode,EnglishLabel,allowAdd);
  }
  if(FieldType==SLI)
  {
      SMin = smin;
      SMax = smax;
  }
  if(FieldType==SLE || FieldType==SLI || FieldType==EC)
  {
     if(FieldType==SLE || FieldType==SLI)
       {
       SLEd = new Simple_LineEdit(parent,pf,fieldCode);
       LE = SLEd;
       }
     if(FieldType==EC)
       {
       LE = ECo->EcLe;
       }
     LE->setEnabled(true);

  }
  if(FieldType==SLI)
  {
    SLid = new QSlider(parent);
    SLid->setMinimum(smin);
    SLid->setMaximum(smax);
    SLid->setValue(smax);
    SLid->setOrientation(Qt::Horizontal);
  }
  if(FieldType==CHB)
  {
    ChB = new QCheckBox(QString(""),parent);
  }
  
}

// method to feed a widget
void FieldClass::Affect(QString text)
{
    if(FieldType==CHB)
    {
        if(text=="true") ChB->setChecked(true);
        else ChB->setChecked(false);
    }
    else
    {
        LE->setText(text);
        if(FieldType==EC) ECo->redoList("");
        if(FieldType == SLI) PFenim->UpdateIndex(text);
    }
}

// method to read an entry
QString FieldClass::GetText()
{
    QString resu = "";
    if(FieldType==CHB)
    {
        if(ChB->isChecked()) resu = "true"; else resu = "";
    }
    else resu = LE->text();
    return(resu);
}

// method to update colour of an entry according to conventions
// this method colors an input area according to rules intended
// to alert users of the origin of the displayed information
void FieldClass::Colour(QString colorText)
{
    if(FieldType==CHB) TitleLabel->setStyleSheet(colorText);
    else LE->setStyleSheet(colorText);
}

// constructor of fenim class - initializations
Fenim::Fenim(QMainWindow *parent,QString repwav,QString nomfi,QDir basejour,bool casa,bool casretr,int typeretraitement,QString suffixe,int vl,int vu,int mf,bool specialCase)
{
    _windowCreated = false;
    ParentWindow = parent;
    PMainWindow=(TadaridaMainWindow *)ParentWindow;
    ACase = casa;
    _reprocessingCase = casretr;
    _reprocessingType = typeretraitement;
    LogVersion = vl;
    UserVersion = vu;
    FrequencyType = mf;
    SpecialCase = specialCase;
    QString logFilePath(QString("fenim")+suffixe+".log");
    _logFile.setFileName(logFilePath);
    _logFile.open(QIODevice::WriteOnly | QIODevice::Text);
    LogStream.setDevice(&_logFile);
    _wavFolder = repwav;
    ReadFolderVersion();
    _mainFileName = nomfi;
    _dayBaseFolder = basejour;
    _dayDatFolder = QDir(basejour.path()+"/dat");
    _dayImaFolder = QDir(basejour.path()+"/ima");
    _deepMode = readDeepMode(repwav);
    // ---
    // 22/03/2021
    _dayImaFolder2 = QDir(basejour.path()+"/ima2");
    // ---
    _dayEtiFolder = QDir(basejour.path()+"/eti");
    _dayTxtFolder = QDir(basejour.path()+"/txt");
    ImageName = _mainFileName + ".jpg";
    ImageFullName = repwav + "/ima/" + ImageName;
    ImageFullName2 = repwav + "/ima2/" + ImageName;
    _datFile = repwav + "/dat/" + _mainFileName + ".dat";
    _da2FileName = repwav + "/dat/" + _mainFileName + ".da2";
    InputToSave = false;
    _filesUpdated = false;
    _overwriteFile = false;
    ShowLoupe = false;
    FactorX = -1;
    _nliv=0;_nlih=0;_nte=0;
    NoMore=false;
    _firstCallSelected = 0;
    _lastCallSelected = 0;
    SpecTagNumber = 0;
    FlagGoodCol = new char[SONOGRAM_WIDTH_MAX];
    FlagGoodColInitial = new char[SONOGRAM_WIDTH_MAX];
    EnergyAverageCol = new char[SONOGRAM_WIDTH_MAX];
    CriLePlusFort = -1;
    EndName = "";
    //Listesp << "Ardcin" << "Erirub" << "Grugru" << "Turili" << "Turmer" << "Turphi";
    //Listesp << "noise" << "wind" ;
    
}


Fenim::~Fenim()
{
    delete[] FlagGoodCol;
    delete[] FlagGoodColInitial;
    delete[] EnergyAverageCol;
    ClearFenim();
    if(_windowCreated) delete PFenimWindow;
}

// this method draws the window
void FenimWindow::CreateFenimWindow(bool modeSaisie)
{
    setWindowTitle("Tadarida  -  Labelling");
    PolText=QFont("Arial",10,QFont::Normal);
    PolTitle=QFont("Arial",10,QFont::Bold);
    _labelImage = new MyQLabel(this);
    gBoxGen = new QGroupBox(this);
    _gGBoxButtons = new QGroupBox(this);
    LabelTitleG2 = new QLabel(gBoxGen);
    _labelMess = new MyQLabel(GBoxInput);
    LabelFolder = new MyQLabel(gBoxGen);
    _labelNbCalls = new MyQLabel(gBoxGen);
    LabelNbLabs = new MyQLabel(gBoxGen);
    LabelTagSpec = new MyQLabel(gBoxGen);
    ChbTagSpec = new QComboBox(gBoxGen);
    _labelCalls = new MyQLabel(gBoxGen);
    EditCall   = new MyQLineEdit((QWidget *)gBoxGen,PFenim,"cry");
    BRightArrow = new MyQPushButton(GBoxInput);
    BLeftArrow = new MyQPushButton(GBoxInput);
    BStartArrow = new MyQPushButton(GBoxInput);
    BEndArrow = new MyQPushButton(GBoxInput);
    BSaveLabels = new MyQPushButton(GBoxInput);
    BClose = new MyQPushButton(GBoxInput);
    BZoom = new MyQPushButton(_gGBoxButtons);
    BUnZoom = new MyQPushButton(_gGBoxButtons);
    BCGrid = new QCheckBox(QString("Grid"),_gGBoxButtons);
    BCMasterPoints = new QCheckBox(QString("Master pts"),_gGBoxButtons);
    BCCalls = new QCheckBox(QString("Lines"),_gGBoxButtons);
    LabelX = new QLabel(_gGBoxButtons);
    LabelY = new QLabel(_gGBoxButtons);
    LabelR = new QLabel(_gGBoxButtons);
    BSaveOneLabel = new MyQPushButton(GBoxInput);
    BSaveOneLabel->setText("Validate the label(s)");
    PrgSessionEnd = new QProgressBar(gBoxGen);
    BRightArrowSpec = new MyQPushButton(gBoxGen);
    BLeftArrowSpec = new MyQPushButton(gBoxGen);
    BStartArrowSpec = new MyQPushButton(gBoxGen);
    BEndArrowSpec = new MyQPushButton(gBoxGen);
    if(!modeSaisie)
    {
        BSaveOneLabel->setEnabled(false);
        BSaveLabels->setEnabled(false);
    }
    _labelImage->setText(PFenim->ImageName);
    QSizePolicy sizePolicy1(QSizePolicy::Expanding, QSizePolicy::Expanding);
    sizePolicy1.setHeightForWidth(GBoxInput->sizePolicy().hasHeightForWidth());
    GBoxInput->setSizePolicy(sizePolicy1);
    GBoxInput->setStyleSheet(QString::fromUtf8(""));
    int typ;
    for(int iField=0;iField<NBFIELDS;iField++)
    {
        typ=PFenim->PFC[iField]->FieldType;
        if(typ==EC || typ==SLI || typ==SLE)
        {
            PFenim->PFC[iField]->LE->setText("");
        }
        if(PFenim->PFC[iField]->FieldType==EC)
        {
            PFenim->PFC[iField]->ECo->EcCo->setFrame(true);
        }
    }
    _labelMess->SetText("");
    BRightArrow->setIcon(QIcon("fleche_droite.jpg"));
    BLeftArrow->setIcon(QIcon("fleche_gauche.jpg"));
    BEndArrow->setIcon(QIcon("fleche_fin.jpg"));
    BStartArrow->setIcon(QIcon("fleche_debut.jpg"));
    BSaveLabels->setText("Save the labels file");
    BSaveLabels->setFont(QFont("Arial",10,QFont::Bold));
    BClose->setText("Close");
    gBoxGen->setSizePolicy(sizePolicy1);
    gBoxGen->setStyleSheet(QString::fromUtf8(""));
    PrgSessionEnd->setMaximum(10000);
    PrgSessionEnd->setValue(0);
    PrgSessionEnd->setTextVisible(false);
    _labelNbCalls->SetText(QString::number(PFenim->CallsNumber)+" Sound events");
    if(PFenim->LabelsNumber>1) LabelNbLabs->SetText(QString::number(PFenim->LabelsNumber)+" labels");
    else LabelNbLabs->SetText(QString::number(PFenim->LabelsNumber)+" label");
    BStartArrowSpec->setIcon(QIcon("fleche_debut.jpg"));
    BEndArrowSpec->setIcon(QIcon("fleche_fin.jpg"));
    BRightArrowSpec->setIcon(QIcon("fleche_droite.jpg"));
    BLeftArrowSpec->setIcon(QIcon("fleche_gauche.jpg"));
    _labelCalls->setText("Sound event(s)");
    EditCall->setText("");
    BZoom->setText("Zoom +");
    BUnZoom->setText("Zoom -");
    BCGrid->setChecked(true);
    BCMasterPoints->setChecked(true);
    BCCalls->setChecked(false);
    PFenim->ShowRatio();
    GBoxInput->setFont(PolText);
    gBoxGen->setFont(PolText);
    _labelCalls->setFont(PolTitle);
    LabelTitleG2->setFont(PolTitle);
    EditCall->setFont(PolTitle);
    //
    Fenima = new QImage;
    Fenima->load(PFenim->ImageFullName);
    Scene = new MyQGraphicsScene(PFenim,this,false); 
    View = new MyQGraphicsView(this); 
    View->setScene(Scene);  
    PixMap=(Scene->addPixmap(QPixmap::fromImage(*Fenima))); 
    View->setMouseTracking(true);
    PFenim->LogStream  << "end of CreateFenimWindow" << endl;
}

// this method creates a FenimWindow object and calls PFenimWindow::CreateFenimWindow
// which draws the window
void Fenim::CreatFenimWindow(bool inputMode)
{
    LogStream << "CreatFenimWindow : cr�ation de PFenimWindow" << endl;
    PFenimWindow = new FenimWindow(this,ParentWindow);
    PFC[ESPECE]       = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Species",EC,true,false,"especes",true,0,0,"species");
    PFC[TYPE]         = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Type",EC,true,false,"types",false,0,0,"type");
    PFC[INDICE]       = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Confidence",SLI,true,false,"indice",false,1,5,"index");
    PFC[ZONE]         = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Region",EC,false,true,"zone",true,0,0,"region");
    PFC[SITE]         = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Site",SLE,false,true,"site",false,0,0,"site");
    PFC[COMMENTAIRE]  = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Comment",false,SLE,false,"comment",false,0,0,"comment");
    PFC[MATERIEL]     = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Recorder",EC,false,true,"materiel",true,0,0,"recorder");
    PFC[CONFIDENTIEL] = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Confidential",CHB,false,true,"confidential",false,0,0,"confidential");
    PFC[DATENREG]     = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Date",SLE,false,true,"datenreg",false,0,0,"date");
    PFC[AUTEUR]       = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Author",EC,false,true,"auteur",true,0,0,"author");
    PFC[ETIQUETEUR]   = new FieldClass((QWidget *)PFenimWindow->GBoxInput,this,"Labeller",EC,false,false,"etiqueteur",true,0,0,"labeller");
    PFenimWindow->CreateFenimWindow(inputMode);
    InputColors[0]=QString("QLineEdit {color: blue;}");
    InputColors[1]=QString("QLineEdit {color: red;}");
    InputColors[2]=QString("QLineEdit {color: green;}");
    InputColors[3]=QString("QLineEdit {color: orange;}");
    InputColors[4]=QString("QLineEdit {color: black;}");
    _windowCreated = true;
}

// this method positions and sizes the graphic objects of the window
void FenimWindow::ResizeFenimWindow(bool firstCall)
{
    _countResize ++;
    if(_countResize < 2) return;
    _fWmx = 10 ; _fWmy=12;
    _fWbh = 18;
    _fWl = width();
    _fWh= height();
    WinRect = geometry();
    int hv = ((_fWh - _fWmy*4 - _fWbh)*2)/3;
    int lv = _fWl - _fWmx*2;
    View->move(_fWmx,_fWmy);
    View->setFixedSize(lv,hv);
    WidthRatio =   (float)_fWh * (1+PFenim->XHalf) / (float)(PFenim->PMainWindow->Divrl);
    HeightRatio = ((float)hv * PFenim->ImageHeight) / ((float)Fenima->height() * 160);
    if(!_alreadyScaled)
    {
        _alreadyScaled = true;
        PFenim->LogStream << "_fWl = " << _fWl << " et __fWh=" << _fWh << endl;
        PFenim->LogStream << "_ WidthRatio = " <<  WidthRatio << " et HeightRatio=" <<  HeightRatio << endl;
        PFenim->LogStream << "PFenim->ImageHeight = " << PFenim->ImageHeight << " et Fenima->height()=" << Fenima->height() << endl;
        View->SCALE(WidthRatio,HeightRatio);
        PFenim->ShowGrid(true);
        PFenim->ShowCalls();
        PFenim->ShowMasterPoints();
        PFenim->SelectCall(0,false);
    }
    int yc = PFenim->ImageHeight + PFenim->ImageHeight - 121;
    View->centerOn(0,yc);
    int hb = (_fWh - _fWmy*4 - _fWbh)/3;
    int lb = (_fWl - _fWmx*3)/2;
    int lbn = _fWl - _fWmx*2;
    int hbg = (hb-_fWmy)/3;
    int hbs = hb-_fWmy-hbg;
    int espgb = _fWmx*2;
    int larbl = ((lbn-espgb*5)*2)/9;
    _labelImage->move(_fWmy,_fWmy/2-7);
    _labelImage->resize(500,15);
    GBoxInput->resize(lbn,hbs);
    GBoxInput->move(_fWmx,_fWh-hb+hbg);
    _gGBoxButtons->resize(_fWl - _fWmx*2,_fWbh+_fWmy);
    _gGBoxButtons->move(_fWmx,_fWh-hb-_fWmy*2-_fWmy/2-_fWbh);
    int hpz = 17;
    int hgz = 21;
    int margx = 15;
    int margx2 =10;
    int larlabel = (lb-margx*4)/4;
    int laredit = ((lb-margx*4)*3)/8;
    int larcombo = laredit;
    int espy = (hbs- hpz*7)/10;
    int col,lig,typ;

    for(int iField=0;iField<NBFIELDS;iField++)
    {
        if(iField<(NBFIELDS+1)/2) {col=0;lig=iField;}
        else {col=1; lig=iField-(NBFIELDS+1)/2;}
        typ=PFenim->PFC[iField]->FieldType;
        PFenim->PFC[iField]->TitleLabel->move(margx+col*(lbn/2),hpz*lig+espy*(1+lig));
        PFenim->PFC[iField]->TitleLabel->resize(larlabel,hpz);
        if(typ==EC || typ==SLI || typ==SLE)
        {
            PFenim->PFC[iField]->LE->move(margx*2+larlabel+col*(lbn/2),hpz*lig+espy*(1+lig));
            PFenim->PFC[iField]->LE->resize(laredit,hpz);
        }
        if(PFenim->PFC[iField]->FieldType==EC)
        {
            PFenim->PFC[iField]->ECo->EcCo->move(margx*3+larlabel+laredit+col*(lbn/2),hpz*lig+espy*(1+lig));
            PFenim->PFC[iField]->ECo->EcCo->resize(larcombo,hpz);
        }
        if(PFenim->PFC[iField]->FieldType==SLI)
        {
            PFenim->PFC[iField]->SLid->move(margx*3+larlabel+laredit+col*(lbn/2),hpz*lig+espy*(1+lig));
            PFenim->PFC[iField]->SLid->resize(larcombo,hpz);
        }
        if(PFenim->PFC[iField]->FieldType==CHB)
        {
            PFenim->PFC[iField]->ChB->move(margx*3+larlabel+laredit+col*(lbn/2),hpz*lig+espy*(1+lig));
            PFenim->PFC[iField]->ChB->resize(larcombo,hpz);
        }
    }
    _labelMess->move(margx+lbn/2,hpz*5+espy*6);
    _labelMess->resize(larlabel+laredit+larcombo+margx*2,hpz);
    int lpb = hgz;
    BRightArrow->move(margx,hpz*6+espy*7);
    BRightArrow->resize(lpb,hgz);
    BLeftArrow->move(margx*2+lpb,hpz*6+espy*7);
    BLeftArrow->resize(lpb,hgz);
    BEndArrow->move(margx*3+lpb*2,hpz*6+espy*7);
    BEndArrow->resize(lpb,hgz);
    BStartArrow->move(margx*4+lpb*3,hpz*6+espy*7);
    BStartArrow->resize(lpb,hgz);
    BSaveLabels->move(espgb*3+larbl*2,hpz*6+espy*7);
    BSaveLabels->resize((larbl*3)/2,hgz);
    BSaveOneLabel->move(espgb*2+larbl,hpz*6+espy*7);
    BSaveOneLabel->resize(larbl,hgz);
    BClose->move(espgb*4+(larbl*7)/2,hpz*6+espy*7);
    BClose->resize(larbl,hgz);
    int espy2 = (hbg- hpz*3)/4;
    gBoxGen->resize(lbn,hbg);
    gBoxGen->move(_fWmx,_fWh-hb-_fWmy);
    LabelTitleG2->move(margx,espy2);
    LabelTitleG2->resize((lbn-margx*3)/2,hpz);
    LabelFolder->move(margx+lbn/2,espy2);
    LabelFolder->resize((lbn-margx*3)/2,hpz);
    PrgSessionEnd->move(margx+lbn/2,espy2);
    PrgSessionEnd->resize(0,0);
    _labelNbCalls->move(margx,hpz+espy2*2);
    _labelNbCalls->resize((lbn-margx*3)/2,hpz);
    LabelNbLabs->move(margx+lbn/2,hpz+espy2*2);
    LabelNbLabs->resize((lbn-margx*3)/2,hpz);
    int mxl = 5;
    int wts = (lbn-margx*3)/2-mxl*3;
    int lw = (wts*2)/9;
    int gw = wts/3;
    int db = gw/4;
    int xdep = margx+lbn/2;
    int yl= hpz+espy2*2;
    ChbTagSpec->move(xdep+lw+mxl,yl);
    ChbTagSpec->resize(lw,hpz);
    LabelTagSpec->move(xdep+lw*2+mxl*2,yl);
    LabelTagSpec->resize(lw,hpz);
    BStartArrowSpec->move(xdep+lw*3+mxl*3,yl);
    BStartArrowSpec->resize(lpb,hgz);
    BEndArrowSpec->move(xdep+lw*3+mxl*3+db,yl);
    BEndArrowSpec->resize(lpb,hpz);
    BRightArrowSpec->move(xdep+lw*3+mxl*3+db*2,yl);
    BRightArrowSpec->resize(lpb,hpz);
    BLeftArrowSpec->move(xdep+lw*3+mxl*3+db*3,yl);
    BLeftArrowSpec->resize(lpb,hpz);
    _labelCalls->move(margx,hpz*2+espy2*3);
    _labelCalls->resize((larlabel*2)/3,hgz);
    EditCall->move(margx*2+(larlabel*2)/3,hpz*2+espy2*3);
    EditCall->resize(lbn-margx*3-((larlabel*2)/3),hgz);
    int lzb = _gGBoxButtons->width();
    int larpw = (lzb-margx2*13)/12;
    BZoom->move(margx2,_fWmy/4);
    BZoom->resize(larpw,_fWbh);
    BUnZoom->move(margx2*2+larpw,_fWmy/4);
    BUnZoom->resize(larpw,_fWbh);
    BCGrid->move(margx2*3+larpw*2,_fWmy/4);
    BCGrid->resize(larpw,_fWbh);
    BCMasterPoints->move(margx2*4+larpw*3,_fWmy/4);
    BCMasterPoints->resize(larpw,_fWbh);
    BCCalls->move(margx2*5+larpw*4,_fWmy/4);
    BCCalls->resize(larpw,_fWbh);
    LabelX->move(lzb - margx2 * 2 - larpw * 2,_fWmy/4);
    LabelY->move(lzb - margx2 - larpw,_fWmy/4);
    LabelR->move(lzb - margx2  * 3 - larpw*3,_fWmy/4);
    LabelX->resize(larpw,_fWbh);
    LabelY->resize(larpw,_fWbh);
    LabelR->resize(larpw,_fWbh);
}

// this method displays the information offered in each field and colors them
// according to rules described in the manual
void Fenim::initInputs()
{
    for(int i=0;i<NBFIELDS;i++)
    {
        if(PFC[i]->Unic) FileFields[i]="";
    }
    for(int i=0;i<CallsNumber;i++)
    {
        if(!EtiquetteArray[i]->DataFields[ESPECE].isEmpty())
        {
            for(int j=0;j<NBFIELDS;j++)
            {
                if(PFC[j]->Unic)
                {
                    FileFields[j] = EtiquetteArray[i]->DataFields[j];
                    PMainWindow->LastFields[j] = FileFields[j];
                }
            }
            break;
        }
    }
    for(int i=0;i<NBFIELDS;i++)
    {
        PFC[i]->Affect(PMainWindow->LastFields[i]);
        PFC[i]->Colour(InputColors[0]);
    }
}

// method used by the Loupe class to know location and dimensions of fenim window
QRect Fenim::GetWindowRect()
{
    return(PFenimWindow->WinRect);
}

// method used to give information to Loupe class object
QImage * Fenim::GetImage()
{
    return(PFenimWindow->Fenima);
}

// this method selects a sound events which number is entered in EditLabel widget
void Fenim::SelectEditedCalls()
{
    if(NoMore) return;
    QString cs=PFenimWindow->EditCall->text();
    bool ok=true;
    int n=1;
    if(cs.length()==0) ok=false;
    else
    {
        bool convint;
        n = cs.toInt(&convint);
        if(convint==false) ok=false;
        else
        {
            if(n<1 || n>CallsNumber) ok=false;
        }
    }
    if(ok==false)
    {
        PFenimWindow->EditCall->setText(_callsString);
    }
    else
    {
        if(cs!=_callsString) SelectCall(n-1,false);
    }
}


// this method updates LineEdit object associated with a SlideBox object according
// to the value transmitted
void Fenim::SelectIndex(int n)
{
    PFC[INDICE]->LE->setText(QString::number(n));
    PFC[INDICE]->LE->setStyleSheet(InputColors[4]);
}

// this method updates the SlideBox object according to value transmitted
void Fenim::UpdateIndex(const QString& selectedIndex)
{
    bool convint;
    int nind = selectedIndex.toInt(&convint);
    if(convint)
    {
        if(nind>0 && nind<6)
            PFC[INDICE]->SLid->setValue(nind);
    }
}

void Fenim::ClickConfi()
{
    PFC[CONFIDENTIEL]->Colour(InputColors[4]);
}

// this method controls a text entered in the QLineEdit object of an EditCombo object
bool EditCombo::Control(QString &s,QString &errorMessage,bool obl)
{
    bool bon = true; errorMessage="";
    s=EcLe->text();
    if(s.isNull() || s.isEmpty())
    {
        if(obl==true)
        {
            bon = false;
            errorMessage="You must entry code " + EnglishCode + " !";
        }
        else
        {
            bon=true;
        }
    }
    else
    {
        if(!ListCodes->contains(s))
        {
            if(!AllowAdd)
            {
                bon = false;
                errorMessage = "Unauthorized code !";
            }
            else
            {
                if(!ConfirmAdd(s))
                    bon = false;
            }
        }
    }
    if(!bon)
    {
        EcLe->clear();
        redoList("");
        EcLe->setFocus();
    }
    return(bon);
}

// this method saves in memory labels (created or updated)
// for the sound event(s) selected
// when the button "Validate the label(s)" is pressed
void Fenim::ValidateLabel()
{
    QString s,mess_err="";
    for(int i=0;i<NBFIELDS;i++)
    {
        s=PFC[i]->GetText();
        if(s.isEmpty() && PFC[i]->Obl==true)
        {
            QMessageBox::warning(PFenimWindow,"Required entry",mess_err, QMessageBox::Ok);
            PFC[i]->LE->setFocus();
            return;
        }
        if(PFC[i]->FieldType==EC)
        {
            if(!PFC[i]->ECo->Control(s,mess_err,true))
            {
                QMessageBox::warning(PFenimWindow,"Incorrect entry",mess_err, QMessageBox::Ok);
                PFC[i]->ECo->EcLe->setFocus();
                return;
            }
        }
        if(PFC[i]->FieldType==SLI && !s.isEmpty())
        {
            bool convint;
            int nind = PFC[i]->GetText().toInt(&convint);
            if(convint)
            {
                if(nind<PFC[i]->SMin || nind>PFC[i]->SMax) convint=false;
            }

            if(!convint)
            {
                QMessageBox::warning(PFenimWindow,"Incorrect entry","Enter a number between 1 and 5 !", QMessageBox::Ok);
                PFC[i]->LE->setFocus();
                return;
            }
        }
    }
    QString dae= PFC[DATENREG]->GetText();
    if(!dae.isEmpty())
    {
        QString sj=dae.section("/",0,0);
        QString sm=dae.section("/",1,1);
        QString sa=dae.section("/",2,2);
        bool convdate=false;
        bool convj,convm,conva;
        int j = sj.toInt(&convj);
        int m = sm.toInt(&convm);
        int a = sa.toInt(&conva);
        if(convj && convm && conva)
        {
            convdate=QDate(a,m,j).isValid();
        }
        if(!convdate)
        {
            QMessageBox::warning(PFenimWindow,"Enter a date dd/mm/yyyy",mess_err, QMessageBox::Ok);
            PFC[DATENREG]->LE->setFocus();
            return;
        }
    }
    // -----
    int premi=-1;
    for(int i=0;i<CallsNumber;i++)
    {
        if(SelectedCalls[i])
        {
            if(premi<0) premi=i;
            if(EtiquetteArray[i]->DataFields[ESPECE].isEmpty()) LabelsNumber++;
            for(int j=0;j<NBFIELDS;j++)
                EtiquetteArray[i]->DataFields[j]= this->PFC[j]->GetText();
            updateTagNSpec(i);
        }
    }
    if(!_reprocessingCase && !SpecialCase)
    {
        inputsSave(EtiquetteArray[premi]);
        greenPaint();
        treatUniqueFields();
        TadaridaMainWindow *tg=(TadaridaMainWindow *)ParentWindow;
        tg->TextsToSave = true;
        showNbLabels();
        updateChbTagSpec();
    }
    InputToSave = true;
}

// this method saves last entered text to offer them for the next entries
void Fenim::inputsSave(Etiquette *pLabel)
{
    for(int i=0;i<NBFIELDS;i++)
        PMainWindow->LastFields[i] = pLabel->DataFields[i];
}

// this method affects the values entered for one (or more) sound events
// to all the sound events, for the fields which must have the same value
// for the whole file
void Fenim::treatUniqueFields()
{
    bool toExtend = false;

    for(int jField=0;jField<NBFIELDS;jField++)
    {
        if(PFC[jField]->Unic)
        {
            if(FileFields[jField] != PMainWindow->LastFields[jField])
            {
                FileFields[jField] = PMainWindow->LastFields[jField];
                toExtend = true;
            }
        }
    }
    if(toExtend)
    {
        for(int i=0;i<CallsNumber;i++)
        {
            if(!SelectedCalls[i] && !EtiquetteArray[i]->DataFields[ESPECE].isEmpty())
            {
                for(int jField=0;jField<NBFIELDS;jField++)
                    if(PFC[jField]->Unic) EtiquetteArray[i]->DataFields[jField] = FileFields[jField];
            }
        }
    }
}

// colors in green colour inputs which have already been saved
void Fenim::greenPaint()
{
    for(int j=0;j<NBFIELDS;j++) PFC[j]->Colour(InputColors[2]);
}

// this method loads useful informations (.da2 file)
// and shows the window, created by the call of CreatFenimWindow method
// this is the entry point of the fenim class
// it is called by the showPicture method of the main class
bool Fenim::ShowFenim(bool inputMode)
{
    if(FolderLogVersion <LogVersion || FolderUserVersion < UserVersion)
    {
        QString mess = QString("flv=")+QString::number(FolderLogVersion)
                               +"  lv="+QString::number(LogVersion)
                               +"  fuv="+QString::number(FolderUserVersion)
                               +"  uv="+QString::number(UserVersion);

        QMessageBox::warning(ParentWindow,"File is unreacheable","Version is late : reprocess first the folder !", QMessageBox::Ok);
        QMessageBox::warning(ParentWindow,"File is unreacheable",mess, QMessageBox::Ok);
        return(false);
    }
    initCalls();
    if(loadCallsMatrices(_da2FileName)==false)
    {
        QMessageBox::warning(ParentWindow,"File is unreacheable :"," .da2 File not found or late : reprocess first the folder", QMessageBox::Ok);
        return(false);
    }
    _windowOpen = true;
    CreatFenimWindow(inputMode);
    if(loadLabels()==false)
    {
        if(_windowCreated) PFenimWindow->close();
        return(true);
    }
    showNbLabels();
    initInputs();
    initMasterPoints();
    initLines();
    PFenimWindow->CreateConnections();
    PFenimWindow->showMaximized();
    PFenimWindow->activateWindow();
    PFenimWindow->raise();
    return(true);
}

// this method is used by methods of the RematchClass class
// to get informations useful for general reprocessing
bool Fenim::LoadCallsLabels()
{
    LogStream << "lcl debut" << endl;

    if(!_reprocessingCase  && !SpecialCase) initCalls();
    LogStream << "lcl 2" << endl;
    if(loadCallsMatrices(_da2FileName)==false)
    {
        LogStream << "lcl 3" << endl;
        _windowOpen = false;
        return(false);
    }
    else
    {
        LogStream << "lcl 4" << endl;
        _windowOpen = true;
    }
    LogStream << "lcl 5" << endl;
    if(loadLabels()==false)
    {
        LogStream << "lcl 6" << endl;
        return(false);
    }
    LogStream << "lcl 7" << endl;
    return(true);
}

// these methods manage the zoom of the picture
void Fenim::Zoom()
{
    ZoomF(1.414f);
}
void Fenim::UnZoom()
{
    ZoomF(0.707f);
}
void Fenim::ZoomF(float iz)
{
    PFenimWindow->View->SCALE(iz,1);
    PFenimWindow->WidthRatio *= iz;
    ShowGrid(PFenimWindow->BCGrid->isChecked());
    ShowMasterPoints();
    ShowRatio();
}

// this method initializes vectors which get informations about sound events
// used to manage the display of sound events in the picture
void Fenim::initCalls()
{
    for(int i=0;i<CRESTSNUMBER;i++)
    {
        CallsMatrix[i].clear();
        for(int j=0;j<NSUPPL;j++) AddPointsVector[i][j].clear();
    }
    MasterPointsVector.clear();
    ContoursMatrices.clear();

}

// this method draws a sound event
// it calls ShowOneCall for each sound event
void Fenim::ShowCalls()
{
    bool affichercri = PFenimWindow->BCCalls->isChecked();
    for(int i=0;i<CallsNumber;i++)
    {
        ShowOneCall(i,SelectedCalls[i],affichercri);
    }
}

// this method displays the representation of "master points"
// (peaks of energy of sound events)
void Fenim::ShowMasterPoints()
{
    bool afficherpm = PFenimWindow->BCMasterPoints->isChecked();
    for(int i=0;i<CallsNumber;i++) ShowOneMasterPoint(i,SelectedCalls[i],afficherpm);
}

void Fenim::ActivateGrid(int state)
{
    ShowGrid(state==Qt::Checked);
}

void Fenim::ActivateMasterPoints()
{
    ShowMasterPoints();
}

void Fenim::ActivateCrests()
{
    ShowCalls();
}

// this method displays or hides the grids (graduations)
void Fenim::ShowGrid(bool toShow)
{
    if(_nliv>0) for(int i=0;i<_nliv;i++) delete PFenimWindow->GLiv[i];
    if(_nlih>0) for(int i=0;i<_nlih;i++) delete PFenimWindow->GLih[i];
    if(_nte>0) for(int i=0;i<_nte;i++) delete PFenimWindow->GTe[i];
    _nliv=0; _nlih=0; _nte=0;
    if(!toShow) return;

    float invsx = 1.0f/PFenimWindow->WidthRatio;
    float invsy = 1.0f/PFenimWindow->HeightRatio;
    QFont qf("Arial",8);
    int xmax=PFenimWindow->Fenima->width();
    float tmax = Getms(xmax-1);
    float igt=0;
    float incrt = 500;
    if(PFenimWindow->WidthRatio>0.25) incrt = 100;

    QPen qp = QPen(QColor(128,128,128),0);
    while(igt<tmax && _nliv < 500 && _nte<250)
    {
        float x=GetX(igt);
        PFenimWindow->GLiv[_nliv] = PFenimWindow->Scene->addLine(x,0,x,ImageHeight-1,qp);
        if((_nliv & 1)==0 && _nliv>0)
        {
            int nigt =(int)igt; int ns = nigt/1000;
            QString affi;
            if(nigt == ns * 1000) affi = QString::number(ns)+" sec";
            else affi = QString::number(nigt)+" ms";
            PFenimWindow->GTe[_nte] = PFenimWindow->Scene->addSimpleText(affi,qf);
            PFenimWindow->GTe[_nte]->setPos(x+invsx*2,ImageHeight-((float)30/PFenimWindow->HeightRatio));
            PFenimWindow->GTe[_nte]->SCALE(invsx,invsy);
            _nte++;
        }
        _nliv++;
        igt += incrt;
    }
    float fmax = GetkHz(0);
    float igf=0;
    float incrf = 10;
    while(igf<fmax && _nlih < 500)
    {
        float y=GetY(igf);
        PFenimWindow->GLih[_nlih] = PFenimWindow->Scene->addLine(0,y,xmax-1,y,qp);
        if((_nlih & 1)==0 && _nlih>0)
        {
            PFenimWindow->GTe[_nte] = PFenimWindow->Scene->addSimpleText(QString::number(igf)+" kHz",qf);
            PFenimWindow->GTe[_nte]->setPos(1+invsx,y-8+PFenimWindow->HeightRatio);
            PFenimWindow->GTe[_nte]->SCALE(invsx,invsy);
            _nte++;
        }
        _nlih++; igf += incrf;
    }
}

// this method draws the representation of one sound event
void Fenim::ShowOneCall(int callNumber,bool selectedCall,bool showCall)
{
    if(!(callNumber<MAXCRI)) return;
    bool etiquette = !EtiquetteArray[callNumber]->DataFields[ESPECE].isEmpty();
    QPen qp = QPen(QColor(
                       (255-80*etiquette)*(!selectedCall)+20*selectedCall*etiquette,
                       (255-100*etiquette)*(!selectedCall),
                       255*(!selectedCall)+80*selectedCall*etiquette),
                       0);
    if(!showCall)
    {
        if(_ilc[callNumber])
        {
            delete PFenimWindow->GPlt[callNumber];
            _ilc[callNumber]=false;
        }
    }
    else
    {
        if(!_ilc[callNumber])
        {
            QPolygonF polygone;
            for(int j=0;j<CallsMatrix[0][callNumber].size();j++)
            {
                int x=CallsMatrix[0][callNumber][j].x()/(1+XHalf);
                int y=ImageHeight-CallsMatrix[0][callNumber][j].y()-1;
                polygone << QPointF(x,y);
            }
            QPainterPath path = QPainterPath();
            path.addPolygon(polygone);
            PFenimWindow->GPlt[callNumber] = new QGraphicsPathItem(path);
            PFenimWindow->GPlt[callNumber]->setPen(qp);
            PFenimWindow->Scene->addItem(PFenimWindow->GPlt[callNumber]);
            _ilc[callNumber]=true;
        }
        else
        {
            int counou=(int)etiquette*2+(int)selectedCall;
            if(counou!=_callColour[callNumber])
            {
                PFenimWindow->GPlt[callNumber]->setPen(qp);
                _callColour[callNumber]=counou;
            }
        }
    }
}

// this method draws the representation of one master point
void Fenim::ShowOneMasterPoint(int callNumber,bool selectedCall,bool showMasterPoint)
{
    if(!(callNumber<MAXCRI)) return;
    int x = MasterPointsVector[callNumber].x()/(1+XHalf);
    int y = ImageHeight - MasterPointsVector[callNumber].y()-1;

    bool etiquette = !EtiquetteArray[callNumber]->DataFields[ESPECE].isEmpty();
    int nspec= (EtiquetteArray[callNumber]->SpecNumber);
    int rouge,vert,bleu,ajdec;
    bleu=0;
    ajdec=0;
    if(nspec>=8) nspec = nspec & 7;
    if(nspec>4) {nspec-=4; ajdec=1;}
    if(selectedCall)
    {
        rouge=0;vert=0;
        if(etiquette) {vert=16*nspec;rouge=8*nspec;}
    }
    else
    {
        rouge=255;vert=0;
        if(etiquette)
        {vert=255-50*nspec+32*ajdec;rouge=50*nspec+32*ajdec;}
    }
    QPen qpm = QPen(QColor(rouge,vert,bleu),0);
    QBrush qb = QBrush(QColor(rouge,vert,bleu),Qt::SolidPattern);
    if(_ipmc[callNumber]==true)
    {
        delete PFenimWindow->GEpm[callNumber];
        _ipmc[callNumber]=false;
    }
    if(showMasterPoint)
    {
        if(_ipmc[callNumber]==false)
        {
            // float w=3.0f/m_rl+m_rl/16;
            // float h=2.0f/m_rh+m_rh/16;
            float w=6.0f/PFenimWindow->WidthRatio;
            float h=6.0f/PFenimWindow->HeightRatio;
            PFenimWindow->GEpm[callNumber]=PFenimWindow->Scene->addEllipse(x-w/2,y-h/2,w,h,qpm,qb);
            _ipmc[callNumber]=true;
        }
        else PFenimWindow->GEpm[callNumber]->setPen(qpm);
    }
}

// this method loads .da2 file, associated and loads informations from this file in matrices
bool Fenim::loadCallsMatrices(QString da2File)
{
    LogStream << "loadcallmatrices debut" << endl;
    _da2File.setFileName(da2File);
    if(_da2File.open(QIODevice::ReadOnly)==false)
    {
        LogStream << "da2 file is missing : " << da2File << endl;
        if(!_reprocessingCase && !SpecialCase)
        QMessageBox::warning(PFenimWindow, "Error", "da2 file is missing", QMessageBox::Ok);
        return(false);
    }
    _da2Stream.setDevice(&_da2File);
    int numver=0,numveruser=0;
    _da2Stream >> numver;
    if(numver>3) _da2Stream >> numveruser;
    if(numver<11)
    {
        QMessageBox::warning(PFenimWindow, "Error", "da2 file is incompatible with software version", QMessageBox::Ok);
        return(false);
    }
    LogStream << "numver,m_verLog=" << numver << "," << LogVersion << endl;
    LogStream << "numveruser,m_verUser=" << numveruser << "," << UserVersion << endl;
    if(!_reprocessingCase)
    {
        if(numver < LogVersion || numveruser < UserVersion)
        {
            LogStream << "da2 file version is late" << endl;
            LogStream << "numveruser,m_verUser=" << numveruser << "," << UserVersion << endl;
            _da2File.close();
            return(false);
        }
    }
    _da2Stream >> CallsNumber;
    LogStream << " nb calls = " << CallsNumber << endl;
    _da2Stream >> ImageHeight;
    LogStream << " _imaHeight = " << ImageHeight << endl;
    if(numver > 1)
    {
        _da2Stream >> XHalf;
        LogStream << "m_xmoitie = " << XHalf << endl;
    }

    if(numver>2)
    {
        _da2Stream >> FactorX;
        _da2Stream >> FactorY;
        LogStream << "m_factory=" << FactorY << endl;
        LogStream << "m_factorx=" << FactorX << endl;
    }
    NumVer = numver;
    PtE = 10;
    if(numver>19)
    {
        _da2Stream >> PtE;
    }
    else
    {
        NumtE = FactorY * ImageHeight * 2000;
    }
    // -------------------
    int xpointm,ypointm;
    CriLePlusFort = -1;
    EndName = "";
    EnergyMax = 0;
    EnergyMin = 0;
    for(int ijk=0;ijk<NCRISSEL;ijk++)
    {
        CrisLesPlusForts[ijk] = -1;
        CrisLesPlusLongs[ijk] = -1;
    }
    for(int ijk=0;ijk<NCRISSEL * 2;ijk++)
    {
        CrisSel[ijk] = -1;
    }
    for(int ijk=0;ijk<CallsNumber;ijk++)
    {
        Intensites[ijk] = -1;
        Durees[ijk] = -1;
        Frequences[ijk] = -1;
    }


    //double scoreMax = -1;
    //double s = -1;
    //int ympMin = (int)(PMainWindow->CoefSpe)*5;
    int ympMin = (int)(PMainWindow->CoefSpe)*1;
    int ympMax = (int)(PMainWindow->CoefSpe)*50;
    int longMin = (int)(10.0d/(PMainWindow->CoefSpe));


    LogStream << "loadcallmatrices - avant boucle des cris - callsnumbers = " << CallsNumber << endl;

    if(CallsNumber >0 && CallsNumber < MAXCRI)
    for(int i=0;i<CallsNumber;i++)
    {
        _da2Stream >> xpointm;
        _da2Stream >> ypointm;
        QPoint p;
        p.setX(xpointm);
        p.setY(ypointm);
        MasterPointsVector.push_back(p);
        int longCri;
        _da2Stream >> longCri;
        _contoursVector.clear();
        _energyVector.clear();
        int x,y;
        float e;
        float eCall = 0.0f;
        int xmin=6128,xmax=0;
        double yeCall = 0.0f;
        for(int j=0;j<longCri;j++)
        {
            _da2Stream >> x >> y >> e;
            QPoint p;
            p.setX(x);
            p.setY(y);
            _contoursVector.push_back(p);
			
            _energyVector.push_back(e);

            if(x<xmin) xmin = x;
            if(x>xmax) xmax = x;
            if(e>eCall)
            {
                eCall = e;
                yeCall = y;
            }
        }
        LogStream << "cri " << i << "ecall=" << eCall << "longcri=" << longCri << endl;
        /*
        //double cy = 0.0f;
        //if(yeCall > 64 && yeCall < 128) cy = ((double)(128 - yeCall)) / 4.0f;
        //double cw = 0.0f;
        //if(xmax-xmin > 0 && xmax - xmin < 24) cw = (xmax-xmin) / 4.0f;
        //s = eCall - cy - cw;
        if(s > scoreMax)
        {
            scoreMax = s;
            CriLePlusFort = i;
        }
        */
        //if(eCall > EnergyMax && ypointm > 5 && ypointm < 51 && (xmax - xmin) > 10)
        MpIn = (int)(eCall*100.0d);
        MpHz = (int)((double)ypointm * FactorY * 1000.0d);
        MpMs = (int)((double)xpointm * FactorX);
        MDur = (int)((double)(xmax-xmin+0.5) * FactorX);
        LogStream << "sessionfinish : multiplesounds = " << PMainWindow->MultipleSounds << endl;

        if(PMainWindow->MultipleSounds == 1)
        {
            LogStream << "cas multiplesounds - affectation des variables des cris" << endl;
            Intensites[i] = MpIn;
            Frequences[i] = MpHz;
            Temps[i] = MpMs;
            Durees[i] = (int)  ((((double)(xmax-xmin))+0.5) / PMainWindow->CoefSpe);
            EndsNames[i] = QString("--") + QString::number(i)
                    + QString("--") + QString::number(MpIn)
                    + QString("--") + QString::number(MDur)
                    + QString("--") + QString::number(MpHz)
                    + QString("--") + QString::number(MpMs)
                    + ".jpg";
        }
        if(eCall > EnergyMax)
        {
            if(ypointm > ympMin && ypointm < ympMax && (xmax - xmin) > longMin)
            {
                EnergyMax = eCall;
                CriLePlusFort = i;
                EndName = QString("--") + QString::number(CriLePlusFort)
                        + QString("--") + QString::number(MpIn)
                        + QString("--") + QString::number(MpMs)
                        + QString("--") + QString::number(MpHz)
                        + ".jpg";

            }
            else
            {
 LogStream << _mainFileName << " : cri " << i << " recale : ypointm=" << ypointm
           << "xmin,xmax="  << xmin << "," << xmax << endl;
            }
        }
        //
        ContoursMatrices.push_back(_contoursVector);
        EnergyMatrix.push_back(_energyVector);
        int crestLength;
        for(int jcrete=0;jcrete<CRESTSNUMBER;jcrete++)
        {
            _callsVector.clear();
            _da2Stream >> crestLength;
            for(int j=0;j<crestLength;j++)
            {
                _da2Stream >> x >> y;
                QPoint p;
                p.setX(x);
                p.setY(y);
                _callsVector.push_back(p);
            }
            CallsMatrix[jcrete].push_back(_callsVector);

        }
        for(int jcrete=0;jcrete<CRESTSNUMBER;jcrete++)
            for(int k=0;k<NSUPPL;k++)
            {
                _da2Stream >> x >> y;
                QPoint p;
                p.setX(x);
                p.setY(y);
                AddPointsVector[jcrete][k].push_back(p);
            }
    }
    // ------------------------------
    LogStream << "loadcallmatrices vers la fin" << endl;
    Ncs = 0;
    if(PMainWindow->MultipleSounds == 1)
    {
        LogStream << "avant appel sortcallarrays" << endl;

        Ncs = SortCallsArrays();
        LogStream << "sortcallarrays" <<  Ncs << " cris selectionnes" << endl;
        if(Ncs>0)
        {
            for(int j=0;j<Ncs;j++)
            {
                int numcri = CrisSel[j];
                LogStream << (int)(j+1) << ") cri " << numcri << " intensite= " << Intensites[numcri]
                          << " duree = " << Durees[numcri]
                          << " endname = " << EndsNames[numcri] << endl;
            }
        }
    }
    else
    {
        LogStream << "pas d'appel de sortcallarrays : multiplesounds #1 !" << endl;
    }
    // ------------------------------
    if(numver>20)
    {
        _da2Stream >> SonogramWidth;
        int f0;
        _da2Stream >> f0;
        WithSilence = (bool)f0;
        if(WithSilence)
        {
            LogStream << "withSilence=true" << endl;
            for(int j=0;j<SonogramWidth;j++)
            {
                qint8 f1,f2,f3;
                _da2Stream >> f1 >> f2 >> f3;
                FlagGoodCol[j] = f1;
                FlagGoodColInitial[j] = f2;
                EnergyAverageCol[j] = f3;
            }
        }
        else LogStream << "withSilence=false" << endl;
    }
    else WithSilence = false;
    _da2File.close();
    return(true);
}

// this method searches for labels which can be recovered
// if considers that the sound event is the same if the master point has the same
// localization or is very close
int Fenim::MatchLabels(Fenim * fenim1,bool initial,QString recupVersion,int *cpma)
{
    LogStream << "MatchLabels - m_nbcris = " << CallsNumber << endl;
    LogStream << "master points Number = " << MasterPointsVector.size() << endl;
    LogStream << "rematcheEtiquettes - fenim1 master points Number = " << fenim1->MasterPointsVector.size() << endl;
    int nrecup=0;
    QStringList listSpecrecup;
    for(int i=0;i<CallsNumber;i++)
    {
        if(!initial) if(!EtiquetteArray[i]->DataFields[ESPECE].isEmpty()) continue;
        QPoint p = this->MasterPointsVector.at(i);
        int x=p.x(),y=p.y();
        for(int j=0;j<fenim1->MasterPointsVector.size();j++)
        {
            QPoint p1 = fenim1->MasterPointsVector.at(j);
            int x1=p1.x(),y1=p1.y();
            *cpma += (x1+y1);
            int d=(x-x1)*(x-x1)+(y-y1)*(y-y1);
            if(d<20)
            {
                QString esp = fenim1->EtiquetteArray[j]->DataFields[ESPECE];
                if(!esp.isEmpty())
                {
                    LabelsNumber++;
                    EtiquetteArray[i]->EtiquetteClone(fenim1->EtiquetteArray[j]);
                    if(!initial)
                        if(!_listTaggedSpecies.contains(esp))
                            if(!listSpecrecup.contains(esp))
                                listSpecrecup.append(esp);
                    nrecup++;
                }
                break;
            }
        }
    }
    if(listSpecrecup.size()>0)
    {
        for(int i=0;i<listSpecrecup.size();i++)
        {
            QString esp = listSpecrecup.at(i);
            PMainWindow->RetreatText << "Recovered species " << esp << " in the file " << _mainFileName
                          << " of version " << recupVersion << endl;
        }
    }
    return(nrecup);
}

// these methods initialize arrays which are used to know if graphic objects
// are already created
void Fenim::initMasterPoints()
{
    for(int i=0;i<CallsNumber && i<MAXCRI;i++)
        _ipmc[i]=false;
}

void Fenim::initLines()
{
    for(int i=0;i<CallsNumber && i<MAXCRI;i++)
    {
        _ilc[i]=false;
        _callColour[i]=0;
    }
}

// this method feeds the list of species that are associated with at least one
// sound event
void Fenim::updateTagNSpec(int i)
{
    int pos = _listTaggedSpecies.size();
    QString esp = EtiquetteArray[i]->DataFields[ESPECE];
    if(!_listTaggedSpecies.contains(esp)) _listTaggedSpecies.append(esp);
    else pos=_listTaggedSpecies.indexOf(esp);
    EtiquetteArray[i]->SpecNumber = pos;
}

// this method loads the combobox which allows to select all the sound events
// associated with a species
void Fenim::updateChbTagSpec()
{
    PFenimWindow->ChbTagSpec->clear();
    PFenimWindow->ChbTagSpec->insertItems(0,_listTaggedSpecies);
}

// this method loads the informations of the ".eti file"
// if the number of sound events of the last treatment and the one
// of the ".eti file" are not identical : the labels are reinitialized
bool Fenim::loadLabels()
{
    LogStream << "loadLabels - CallsNumber = " << CallsNumber << endl;
    SelectedCalls = new bool[CallsNumber];
    _oldSelectedCalls = new bool[CallsNumber];
    EtiquetteArray = new Etiquette*[CallsNumber];
    LogStream << "loadLabels 2" << endl;
    for(int i=0;i<CallsNumber;i++)
    {
        SelectedCalls[i]=false;
        _oldSelectedCalls[i]=false;
        EtiquetteArray[i]=new Etiquette((int)i);
        EtiquetteArray[i]->EtiquetteClear();
    }
    LogStream << "loadLabels 3" << endl;
    LabelsFolderName = _wavFolder + "/eti";
    LogStream << "loadLabels 4 labelfoldername = " << LabelsFolderName  << endl;
    QDir direti(LabelsFolderName);
    if(!direti.exists()) direti.mkdir(LabelsFolderName);
    // pour version contour
    LabelsFileName = _mainFileName + ".eti";
    _labelsFullFileName = LabelsFolderName + "/" + LabelsFileName;
    _labelsFile.setFileName(_labelsFullFileName);
    _overwriteFile = false;
    int ncrilus=0;
    LabelsNumber = 0;
    if(_reprocessingCase && _reprocessingType == 2)
    {
        _overwriteFile = true;
    }
    else
    {
        LogStream << "loadLabels 4" << endl;
        if(_labelsFile.open(QIODevice::ReadOnly | QIODevice::Text))
        {
            LogStream << "loadLabels 5" << endl;
            _labelsStream.setDevice(&_labelsFile);
            _labelsStream.readLine(); // pour �liminer ligne titre
            LogStream << "loadLabels 6" << endl;
            for(int i=0;i<=CallsNumber;i++)
            {
                LogStream << "loadLabels 7" << endl;
                if(_labelsStream.atEnd()) break;
                QString ligne = (_labelsStream.readLine());
                if(ligne.isNull() or ligne.isEmpty()) break;
                int postab = ligne.indexOf((char)'\t');
                if(postab>0)
                {
                    if(ligne.left(postab) != QString::number(i)) break;
                    ncrilus++;
                    if(i<=CallsNumber-1)
                    {
                        EtiquetteArray[i]->DataFields[ESPECE]=ligne.section('\t',1,1);
                        if(!EtiquetteArray[i]->DataFields[ESPECE].isEmpty())
                        {
                            updateTagNSpec(i);
                            LabelsNumber++;
                        }
                        EtiquetteArray[i]->DataFields[TYPE]=ligne.section('\t',2,2);
                        EtiquetteArray[i]->DataFields[INDICE]=ligne.section('\t',3,3);
                        EtiquetteArray[i]->DataFields[ZONE]=ligne.section('\t',4,4);
                        EtiquetteArray[i]->DataFields[SITE]=ligne.section('\t',5,5);
                        EtiquetteArray[i]->DataFields[COMMENTAIRE]=ligne.section('\t',6,6);
                        EtiquetteArray[i]->DataFields[MATERIEL]=ligne.section('\t',7,7);
                        EtiquetteArray[i]->DataFields[CONFIDENTIEL]=ligne.section('\t',8,8);
                        EtiquetteArray[i]->DataFields[DATENREG]=ligne.section('\t',9,9);
                        EtiquetteArray[i]->DataFields[AUTEUR]=ligne.section('\t',10,10);
                        EtiquetteArray[i]->DataFields[ETIQUETEUR]=ligne.section('\t',11,11);
                    }
                    else break;
                }
                else break;
                LogStream << "loadLabels 8" << endl;
            }
            LogStream << "loadLabels 9" << endl;
            _labelsFile.close();
            LogStream << "loadLabels 10" << endl;

            if(ncrilus != CallsNumber)
            {
                LogStream << "loadLabels 11" << endl;
                LogStream << "ncrilus = " << ncrilus << "CallsNumber=" << CallsNumber << endl;

                if(ncrilus>0)
                {
                    reinitLabels();
                    if(QMessageBox::question(PFenimWindow, "Question", "The labels file does not match: confirm overwriting ?",
                                             QMessageBox::Yes|QMessageBox::No)
                            == QMessageBox::No)
                    {
                        PFenimWindow->close();
                        return(false);
                    }
                }
                _overwriteFile = true;
                LogStream << "loadLabels 12" << endl;
            }
            else
            {
                LogStream << "loadLabels 13" << endl;

                if(!_reprocessingCase  && !SpecialCase) updateChbTagSpec();
                LogStream << "loadLabels 14" << endl;
            }
        }
    }
    LogStream << "loadLabels fin" << endl;
    return(true);
}

void Fenim::showNbLabels()
{
    PFenimWindow->LabelTitleG2->setText(QString("File : ")+LabelsFileName);
    PFenimWindow->LabelFolder->SetText(QString("Folder : ")+LabelsFolderName);
    if(LabelsNumber<2)  PFenimWindow->LabelNbLabs->SetText(QString::number(LabelsNumber)+" label");
    else PFenimWindow->LabelNbLabs->SetText(QString::number(LabelsNumber)+" labels");
}

// reinitialization of labels
void Fenim::reinitLabels()
{
    LabelsNumber=0;
    for(int i=0;i<CallsNumber;i++)
        EtiquetteArray[i]->EtiquetteClear();
}

// this method saves the .eti file
void Fenim::SaveLabels()
{
    LogStream << "SaveLabels" << endl;
    if(_overwriteFile) _labelsFile.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate);
    else _labelsFile.open(QIODevice::WriteOnly | QIODevice::Text);
    _labelsStream.setDevice(&_labelsFile);
    _labelsStream.setRealNumberNotation(QTextStream::FixedNotation);
    _labelsStream.setRealNumberPrecision(6);
    _labelsStream << "Cri\tEspece\tType\tIndice\tZone\tSite\tCommentaire\tMateriel\tConfidentiel\tDate\tAuteur\tEtiqueteur\n";

    LogStream << "SaveLabels2" << endl;
    //QStringList *lesp = PFC[ESPECE]->ECo->ListCodes;
    for (int i = 0 ; i < CallsNumber ; i++)
    {
        _labelsStream << EtiquetteArray[i]->CallNumber << '\t';
        for(int j=0;j<NBFIELDS;j++) _labelsStream << EtiquetteArray[i]->DataFields[j] << '\t';
        _labelsStream << endl;
        if(_deepMode)
        {
            QString species = EtiquetteArray[i]->DataFields[ESPECE];
            if(!species.isEmpty())
            {
                if(PMainWindow->LabelsList.contains(species))
                {
                    // compl�ter EndName comme dans le cas de l'appel automatique...
                    EndName = QString("--") + QString::number(i) + ".jpg";
                    CreateDeepImage(i,species);
                }
            }
        }
    }
    LogStream << "SaveLabels3" << endl;
    //
    _labelsFile.close();
    //
    _filesUpdated = true;
    InputToSave = false;
    _overwriteFile = false;
}

// the array:oldSelecteCalls to compare new and old selections to optimize redisplay
void Fenim::StockSelectedCalls()
{
    for(int i=0;i<CallsNumber;i++) _oldSelectedCalls[i]=SelectedCalls[i];
}

// this method manages the redisplay according to the modified selections
void Fenim::ShowSelections(bool specSelect)
{
    QString lsai[NBFIELDS];
    bool bsai[NBFIELDS],bsai2[NBFIELDS];
    for(int j=0;j<NBFIELDS;j++) {lsai[j]=""; bsai[j]=false; bsai2[j]=false;}
    _callsString = "";
    int nbcrisel = 0;
    if(specSelect) {SpecTagNumber=0; SpecTagSel=-1;}
    bool affichercri = PFenimWindow->BCCalls->isChecked();
    bool afficherpm = PFenimWindow->BCMasterPoints->isChecked();
    bool laffichercri = false;
    bool lafficherpm  = false;
    bool laffichersuppl  = false;
    if(ShowLoupe)
    {
        laffichercri = PLoupe->BcCalls->isChecked();
        lafficherpm  = PLoupe->BcMasterPoints->isChecked();
        laffichersuppl  = PLoupe->BcSuppl->isChecked();
    }
    for(int i=0;i<CallsNumber;i++)
    {
        if(_oldSelectedCalls[i] != SelectedCalls[i])
        {
            ShowOneCall(i,SelectedCalls[i],affichercri);
            ShowOneMasterPoint(i,SelectedCalls[i],afficherpm);
            if(ShowLoupe)
            {
                PLoupe->ShowOneCall(i,SelectedCalls[i],laffichercri);
                PLoupe->ShowOneMasterPoint(i,SelectedCalls[i],lafficherpm);
                PLoupe->ShowOneOtherCrestl(i,laffichersuppl);
                PLoupe->ShowOneOtherPoint(i,laffichersuppl);
            }
        }
        if(SelectedCalls[i])
        {
            nbcrisel++;
            if(nbcrisel == 1)
            {
                _callsString = QString::number(i+1);
                _firstCallSelected = i;
            }
            else _callsString += ","+QString::number(i+1);
            _lastCallSelected = i;
            if(specSelect) SpecTagList[SpecTagNumber++] = i;
            for(int jField=0;jField<NBFIELDS;jField++)
            {
                if(!EtiquetteArray[i]->DataFields[jField].isEmpty())
                {
                    if(bsai[jField]==false)
                    {
                        lsai[jField] = EtiquetteArray[i]->DataFields[jField];
                        PFC[jField]->Affect(lsai[jField]);
                        bsai[jField]=true;
                    }
                    else
                    {
                        if(!PFC[jField]->Unic)
                            if(lsai[jField] != EtiquetteArray[i]->DataFields[jField])
                                bsai2[jField]=true;
                    }
                }

            }
        }
    }
    PFenimWindow->EditCall->setText(_callsString);
    // ----------------------------------------------------------------
    int coul=0;
    for(int jField=0;jField<NBFIELDS;jField++)
    {
        if(bsai[jField])
        {
            if(bsai2[jField]) coul=1; else coul=2;
        }
        else coul=0;
        PFC[jField]->Colour(InputColors[coul]);
    }
}

// this method is called when a sound event is selected
void Fenim::SelectCall(int n,bool specSelect)
{
    StockSelectedCalls();
    for(int j=0;j<CallsNumber;j++)
        if(j==n) SelectedCalls[j]=true;
        else SelectedCalls[j]=false;
    if(!specSelect) clearSpecTagsSelection();
    ShowSelections(false);
    if(ShowLoupe)
    {
        int x = MasterPointsVector[n].x()/(1+XHalf);
        int y = ImageHeight - MasterPointsVector[n].y()-1;
        PLoupe->LoupeView->centerOn(x,y);
    }
}

// these methods select the next, previous, first or last sound event
void Fenim::NextCall()
{
    if(_lastCallSelected<CallsNumber-1)
   {
        SelectCall(_lastCallSelected+1,false);
    }
    else
    {
        SelectCall(_lastCallSelected,false);
    }
}

void Fenim::PreviousCall()
{
    if(_firstCallSelected>0) SelectCall(_firstCallSelected-1,false);
    else SelectCall(_firstCallSelected,false);
}

void Fenim::EndCall()
{
    SelectCall(CallsNumber-1,false);
}

void Fenim::StartCall()
{
    SelectCall(0,false);
}

// these methods select the next, previous, first or last species
void Fenim::SpecTagNext()
{
    if(SpecTagNumber>0)
    {
        if(SpecTagSel>-1 && SpecTagSel<SpecTagNumber-1)
        {
            SpecTagSel++;
            SelectCall(SpecTagList[SpecTagSel],true);
        }
    }
}

void Fenim::SpecTagPrevious()
{
    if(SpecTagNumber>0)
    {
        if(SpecTagSel>0)
        {
            SpecTagSel--;
            SelectCall(SpecTagList[SpecTagSel],true);
        }
    }
}

void Fenim::SpecTagLast()
{
    if(SpecTagNumber>0)
    {
        SpecTagSel=SpecTagNumber-1;
        SelectCall(SpecTagList[SpecTagSel],true);
        enableMoreArrows();
    }
}

void Fenim::SpecTagFirst()
{
    if(SpecTagNumber>0)
    {
        SpecTagSel=0;
        SelectCall(SpecTagList[SpecTagSel],true);
        enableMoreArrows();
    }
}

// this method searches for a sound event whose master point is close to the mouse clic
void Fenim::SelectCall(int x,int y,bool isCTRL)
{
    float distmax = 3000;
    int ntrouve = -1;
    int xr=x*(1+XHalf),yr=ImageHeight-y-1;
    for(int i=0;i<CallsNumber;i++)
    {
        float dist=pow(xr-MasterPointsVector[i].x(),2)+pow(yr-MasterPointsVector[i].y(),2);
        if(dist < distmax)
        {
            ntrouve = i;
            distmax = dist;
        }
    }
    if(ntrouve>=0)
    {
        StockSelectedCalls();
        if(isCTRL)
        {
            SelectedCalls[ntrouve]=!SelectedCalls[ntrouve];
        }
        else
        {
            // cas g�n�ral
            for(int j=0;j<CallsNumber;j++) if(j==ntrouve) SelectedCalls[j]=true;
            else SelectedCalls[j]=false;
        }
        clearSpecTagsSelection();
        ShowSelections(false);
    }
}

// this method sets the text of a bubble when the mouse cursor is close to the master point
// of a sound event
QString Fenim::CalculateBubble(int x,int y)
{
    QString retour("");
    float distmax = 100;
    int ntrouve = -1;
    int xr=x,yr=ImageHeight-y-1;
    if(XHalf) xr*=2;
    for(int i=0;i<CallsNumber;i++)
    {
        float dist=pow(xr-MasterPointsVector[i].x(),2)+pow(yr-MasterPointsVector[i].y(),2);
        if(dist < distmax)
        {
            ntrouve = i;
            distmax = dist;
            //break;
        }
    }
    if(ntrouve>=0)
    {
        QString esp = EtiquetteArray[ntrouve]->DataFields[ESPECE];
        QString typ = EtiquetteArray[ntrouve]->DataFields[TYPE];
        QString ind = EtiquetteArray[ntrouve]->DataFields[INDICE];
        if(!esp.isEmpty() || !typ.isEmpty())
            retour=QString("Sound event ")+QString::number(ntrouve+1)+" : "+esp+" - "+typ+ "    ("+ind+")";
        else
            retour=QString("Sound event ")+QString::number(ntrouve+1)+" : without label";
        retour += " - ";
    }
    if(WithSilence && y<6)
    {
        int xr = x * (1+XHalf);
        if(xr>=0 && xr <SonogramWidth)
        retour += QString(" ( ") + QString::number((int)(EnergyAverageCol[xr])) + " )";

    }
    return(retour);
}

void Fenim::ShowBubble(QString bubbleString)
{
        QToolTip::showText(QCursor::pos(),bubbleString);
}

// this method selects the sound events whose master point is inside
// a rectangle selected with the mouse
void Fenim::SelectCallsRect(int x1,int y1,int x2,int y2,bool isCTRL)
{
    y1 = ImageHeight-y1-1;
    y2 = ImageHeight-y2-1;
    if(XHalf) {x1*=2; x2*=2;}
    StockSelectedCalls();
    if(!isCTRL)
    for(int i=0;i<CallsNumber;i++) SelectedCalls[i]=false;
    for(int i=0;i<CallsNumber;i++)
    {
        int x = MasterPointsVector[i].x();
        int y = MasterPointsVector[i].y();
        if(x>=x1 && x<=x2 && y<=y1 && y>=y2)
        {
            if(isCTRL) SelectedCalls[i] = ! SelectedCalls[i];
            else SelectedCalls[i] = true;
        }
    }
    clearSpecTagsSelection();
    ShowSelections(false);
}

// selection of all sound events (Ctrl A)
void Fenim::SelectAllCalls()
{
    StockSelectedCalls();
    for(int i=0;i<CallsNumber;i++) SelectedCalls[i]=true;
    clearSpecTagsSelection();
    ShowSelections(false);
}

// selection of sound events corresponding to a species
void Fenim::SelectSpecTags(const QString& selectedCode)
{
    PFenimWindow->LabelTagSpec->SetText(selectedCode);
    StockSelectedCalls();
    for(int i=0;i<CallsNumber;i++) SelectedCalls[i]=false;
    for(int i=0;i<CallsNumber;i++)
        if(EtiquetteArray[i]->DataFields[ESPECE]==selectedCode) SelectedCalls[i] = true;
    ShowSelections(true);
    PFenimWindow->BStartArrowSpec->setEnabled(true);
    PFenimWindow->BEndArrowSpec->setEnabled(true);
}

void Fenim::clearSpecTagsSelection()
{
    PFenimWindow->LabelTagSpec->SetText("");
    SpecTagNumber=0;
    PFenimWindow->BStartArrowSpec->setEnabled(false);
    PFenimWindow->BEndArrowSpec->setEnabled(false);
    PFenimWindow->BRightArrowSpec->setEnabled(false);
    PFenimWindow->BLeftArrowSpec->setEnabled(false);
}

void Fenim::enableMoreArrows()
{
    PFenimWindow->BRightArrowSpec->setEnabled(true);
    PFenimWindow->BLeftArrowSpec->setEnabled(true);
}

// this method deletes some objects and arrays of Fenim and FenimWindow objects
void Fenim::ClearFenim()
{
    LogStream << "ClearFenim debut" << endl;
    NoMore=true;
    if(_windowOpen == true)
    {
        if(!_reprocessingCase && SpecialCase==false)
        {
        delete PFenimWindow->Fenima;
        delete PFenimWindow->Scene;
        delete PFenimWindow->View;
        }
        delete SelectedCalls;
        delete _oldSelectedCalls;
        for(int i=0;i<CallsNumber;i++) delete EtiquetteArray[i];
        delete EtiquetteArray;
        if(ShowLoupe) delete PLoupe;
        _windowOpen = false;
    }
    LogStream << "ClearFenim fin" << endl;
}

void Fenim::CloseFenim()
{
    //videfenim();
    PFenimWindow->close();
}

// if labelling has been saved (in case of initial labelling), this method
// moves the wav file and output files (treatment and labelling files)
// in the day folder of the reference database
void Fenim::SessionFinish(bool withIma2,bool v7)
{
    LogStream << "SessionFinish 1" << endl;
    if(_reprocessingCase) return;
    LogStream << "SessionFinish 2" << endl;
    if(!ACase) return;
    LogStream << "SessionFinish 3" << endl;
    bool version_a_ecrire = false;
    if(!_filesUpdated) return;
    LogStream << "SessionFinish 4" << endl;
    if(!_dayBaseFolder.exists())
    {
        _dayBaseFolder.mkdir(_dayBaseFolder.path());
        version_a_ecrire = true;
    }
    LogStream << "daybasefolder=" << _dayBaseFolder.path() << endl;
    if(!_dayDatFolder.exists()) _dayDatFolder.mkdir(_dayDatFolder.path());
    PMainWindow->DayPath = _dayBaseFolder.path();
    LogStream << "daypath=" << PMainWindow->DayPath << endl;
    if(!_dayImaFolder.exists()) _dayImaFolder.mkdir(_dayImaFolder.path());
    if(withIma2)
    {
        if(!_dayImaFolder2.exists()) _dayImaFolder2.mkdir(_dayImaFolder2.path());
    }
    if(!_dayEtiFolder.exists()) _dayEtiFolder.mkdir(_dayEtiFolder.path());
    if(!_dayTxtFolder.exists()) _dayTxtFolder.mkdir(_dayTxtFolder.path());
    QString nomFicWav = _mainFileName+".wav";
    QFile wavFile(_wavFolder+"/"+nomFicWav);
    LogStream << "fichier copie =" << QString(_wavFolder+"/"+nomFicWav) << endl;
    wavFile.copy(_dayBaseFolder.path() + "/" + _mainFileName + ".wav");
    LogStream << "copie sur " << QString(_dayBaseFolder.path() + "/" + _mainFileName + ".wav") << endl;

    QString nomFicTxt = _mainFileName+".ta";
    QFile txtFile(_wavFolder+"/txt/"+nomFicTxt);
    txtFile.copy(_dayTxtFolder.path() + "/" + _mainFileName + ".ta");
    _da2File.copy(_dayDatFolder.path() + "/" + _mainFileName + ".da2");
    _labelsFile.copy(_dayEtiFolder.path() + "/" + _mainFileName + ".eti");
    QFile imaFile(ImageFullName);
    imaFile.copy(_dayImaFolder.path() + "/" + _mainFileName + ".jpg");
    if(withIma2)
    {
        if(v7)
        {
            for(int kc=0;kc<CallsNumber;kc++)
            {

                QString callImage = _wavFolder+"/ima2/"+_mainFileName+"--"+QString::number(kc);
                        //+ "--" + PMainWindow->AutomaticSpecies + ".jpg";
                QFile imaFile2(callImage);
                if(imaFile2.exists())
                {
                    QString sdest =  _dayImaFolder2.path() + "/" + _mainFileName+"--" + QString::number(kc)
                            + "--" + PMainWindow->AutomaticSpecies + ".jpg";
                    imaFile2.copy(sdest);
                    LogStream << "copie de " << callImage << "sur " << sdest << endl;
                }
                else
                {
                    LogStream << "fichier non trouve : " << callImage << endl;
                }
            }

        }
        else
        {
            //QString endName = QString("--") + QString::number(CriLePlusFort) + ".jpg";
            // QString callImage = _wavFolder + "/ima2/" + _mainFileName + endName;
            if(PMainWindow->MultipleSounds == 1)
            {
                LogStream << "withima2 - sessionfinish - cas multiplesounds = 1" << endl;
                if(Ncs >0)
                {
                    for(int k=0;k<Ncs;k++)
                    {
                        int numcri = CrisSel[k];
                        QString callImage = _wavFolder + "/ima2/" + _mainFileName + EndsNames[numcri];
                        QFile imaFile2(callImage);
                        if(imaFile2.exists())
                        {
                            QString sdest =  _dayImaFolder2.path() + "/" + _mainFileName + EndsNames[numcri];
                            imaFile2.copy(sdest);
                            LogStream << "copie de " << callImage << "sur " << sdest << endl;
                        }
                        else
                        {
                            LogStream << "fichier non trouve : " << callImage << endl;
                        }
                    }
                }
            }
            else
            {
                LogStream << "withima2 - sessionfinish - cas MultipleSounds = 0" << endl;
                QString callImage = _wavFolder + "/ima2/" + _mainFileName + EndName;
                QFile imaFile2(callImage);
                if(imaFile2.exists())
                {
                    QString sdest =  _dayImaFolder2.path() + "/" + _mainFileName + EndName;
                    imaFile2.copy(sdest);
                    LogStream << "copie de " << callImage << "sur " << sdest << endl;
                }
                else
                {
                    LogStream << "fichier non trouve : " << callImage << endl;
                }



            }
        }
    }
    //
    wavFile.remove();
    imaFile.remove();
    txtFile.remove();
    _callsFile.remove();
    _labelsFile.remove();
    _da2File.remove();
    if(version_a_ecrire) WriteFolderVersion();
    LogStream << "SessionFinish 5" << endl;
}

void FenimWindow::resizeEvent(QResizeEvent *re)
{
    ResizeFenimWindow(false);
    show();
}

// this method handles closing event
void FenimWindow::closeEvent(QCloseEvent *event)
 {
    if(PFenim->InputToSave)
        //fr if(QMessageBox::question(this, "Question", "Quitter sans sauvegarder les saisies ?",
        if(QMessageBox::question(this, "Question", "Exit without saving labels file ?",
                                 QMessageBox::Yes|QMessageBox::No)
                == QMessageBox::No)
        {
            event->ignore();
            return;
        }
    if(PFenim->ACase) PFenim->SessionFinish();
    PFenim->NoMore=true;
    PFenim->ClearFenim();
    event->accept();

 }

// this method creates a Loupe object, which is a zoom window, triggered by doucbleclic
// useful for visualization and/or selection of sound events
void Fenim::CreateLoupe(int x,int y)
{
    if(ShowLoupe) delete PLoupe;
    PLoupe = new Loupe(this,PFenimWindow,x,y);
    PLoupe->ShowLoupe();
    ShowLoupe = true;
}

float Fenim::GetRatio()
{
    return((PFenimWindow->HeightRatio * FactorX * (1+XHalf)) / (PFenimWindow->WidthRatio * FactorY));
}

void Fenim::ShowRatio()
{
    QString ratio;
    ratio.setNum(GetRatio(),'f',2);
    PFenimWindow->LabelR->setText(QString("r=")+ratio);
}

// this method converts an x value in a time value (ms)
float Fenim::Getms(int x)
{
    return((FactorX * x) * (1+XHalf));
}

// this method converts a time value in an x value
float Fenim::GetX(float t)
{
    return(t/(FactorX * (1+XHalf)));
}

// this method converts an y value in a frequency value
float Fenim::GetkHz(int y)
{
    return(FactorY * (ImageHeight - y -1));
}

// this method converts a frequency value in an y value
float Fenim::GetY(float f)
{
    return((float)ImageHeight - 1 - f/FactorY );
}

// this method manages displays (of Fenim and Loupe windows) when the mouse moves
void MyQGraphicsScene::mouseMoveEvent ( QGraphicsSceneMouseEvent * mouseEvent )
{
    QPointF pos = mouseEvent->lastScenePos();
    int x = pos.x();
    int y = pos.y();
    if(Iloupe)
    {
        if(x>=0 && y>=0 && x<PFenim->GetImage()->width() && y<PFenim->GetImage()->height())
        {
            this->views().size();
            QRectF r = Ploupe->LoupeView->mapToScene(Ploupe->LoupeView->viewport()->geometry()).boundingRect();
            Ploupe->LastCenterX = r.left()+r.width()/2;
            Ploupe->LastCenterY = r.top()+r.height()/2;
        }

    }
    QString bubble = PFenim->CalculateBubble(x,y);
    int xr=x,yr=PFenim->ImageHeight-y-1;
    if(PFenim->XHalf) xr*=2;
    if(y > PFenim->GetImage()->height()-1) y=PFenim->GetImage()->height()-1;
    QString ms,khz;
    ms.setNum(PFenim->Getms(x),'f',0);
    khz.setNum(PFenim->GetkHz(y),'f',2);
    if(bubble.length()>0)
    {
        if(Iloupe) Ploupe->ShowBubble(bubble);
        else PFenim->ShowBubble(bubble);
    }
    PFenim->PFenimWindow->LabelX->setText(ms+" ms");
    PFenim->PFenimWindow->LabelY->setText(khz+" khz");
    if(Iloupe)
    {

        bool pointInShape = false,pIS2=false;
        float ener,ener2;
        int distmax = 10000;
        int nbcf = -1;
        int nbpt = 0;
        for(int i=0;i<PFenim->ContoursMatrices.size();i++)
        {
            float dist=pow(xr-PFenim->MasterPointsVector[i].x(),2)
                    +pow(yr-PFenim->MasterPointsVector[i].y(),2);
            if(dist < distmax)
            {
                QVector<QPoint> unemat = PFenim->ContoursMatrices.at(i);
                for(int j=0;j<unemat.size();j++)
                {
                    if(xr==unemat.at(j).x() && yr==unemat.at(j).y())
                    {
                        pointInShape = true;
                        nbcf = i+1;
                        ener = PFenim->EnergyMatrix[i][j];
                        nbpt++;
                        if(!PFenim->XHalf || nbpt==2) break;
                    }
                    if(PFenim->XHalf)
                    {
                        if(xr+1==unemat.at(j).x() && yr==unemat.at(j).y())
                        {
                            nbcf = i+1;
                            pIS2 = true;
                            ener2 = PFenim->EnergyMatrix[i][j];
                            nbpt++;
                            if(nbpt==2) break;
                        }
                    }
                }
            }
        }
        Ploupe->LabelX->setText(ms+" ms");
        Ploupe->LabelY->setText(khz+" khz");
        QString affi="";
        if(pointInShape || pIS2)
        {
            affi = QString::number(nbcf)+": ";
            if(pointInShape) affi += QString::number(ener);
            else affi += " - ";
            if(PFenim->XHalf)
            {
                affi += QString(" ; ");
                if(pIS2) affi += QString::number(ener2); else affi+= " - ";
            }
        }
        Ploupe->LabelEnergy->setText(affi);
    }
    if(derx>0)
    {
        QPen qp = QPen(QColor(0,0,255),0);
        if(algri) this->removeItem((QGraphicsItem *)gri);
        gri = this->addRect(derx,dery,x-derx,y-dery,qp);
        algri = true;
    }
}

// the MyQGraphicsScene is a class heriting from QGraphicsScene
// used to enable dynamic display of graphic objects offered by Qt classes
MyQGraphicsScene::MyQGraphicsScene(Fenim *pf,QMainWindow *parent,bool il):QGraphicsScene(parent)
{
    Qmaitre = parent;
    Iloupe=il;
    if(il)
    {
        Ploupe = (Loupe *)Qmaitre;
        PFenim = pf;
    }
    else
    {
        PFenim = pf;
    }

    derx=-1;
    dery=-1;
    algri = false;
}

// mouse event handlers managed by MyQGraphicsScene class
void MyQGraphicsScene::mousePressEvent ( QGraphicsSceneMouseEvent * mouseEvent )
{
    QPointF pos = mouseEvent->lastScenePos();
    derx = pos.x();
    dery = pos.y();
}

void MyQGraphicsScene::mouseDoubleClickEvent ( QGraphicsSceneMouseEvent * mouseEvent )
{
    mousePressEvent(mouseEvent);
    QPointF pos = mouseEvent->lastScenePos();
    int x = pos.x();
    int y = pos.y();
    if(Iloupe)
    {
        Ploupe->Zoom(x,y);
    }
    else
    {
        PFenim->CreateLoupe(x,y);
    }
}

void MyQGraphicsScene::mouseReleaseEvent ( QGraphicsSceneMouseEvent * mouseEvent )
{
    if(derx < 0 || dery <0) return;
    if(algri) {this->removeItem((QGraphicsItem *)gri); algri=false;}
    QPointF pos = mouseEvent->lastScenePos();
    Qt::KeyboardModifiers keyMod = QApplication::keyboardModifiers ();
    bool isCTRL = keyMod.testFlag(Qt::ControlModifier);
    if(abs(pos.x()-derx)+abs(pos.y()-dery) < 5)
        PFenim->SelectCall(pos.x(),pos.y(),isCTRL);
    else
    {
        int x1,x2,y1,y2;
        if(derx>pos.x()) {x1=pos.x(); x2=derx;}
        else {x1=derx; x2=pos.x();}
        if(dery>pos.y()) {y1=pos.y(); y2=dery;}
        else {y1=dery; y2=pos.y();}
        PFenim->SelectCallsRect(x1,y1,x2,y2,isCTRL);
    }
    derx = -1; dery = -1;
}

void MyQGraphicsScene::keyPressEvent(QKeyEvent* e)
{
    Qt::KeyboardModifiers keyMod = QApplication::keyboardModifiers ();
    if(keyMod.testFlag(Qt::ControlModifier) && e->key() == 'A') PFenim->SelectAllCalls();
}

// subclass of QLabel
MyQLabel::MyQLabel(QWidget *parent):QLabel(parent)
{
    QMaster = parent;
    setFont(QFont("Arial",10,QFont::Normal));
    setStyleSheet("background-color: #F8F8FE");
}

void MyQLabel::SetText(QString message)
{
    if(message.isEmpty())
    {
        if(isVisible()) setVisible(false);
    }
    else
    {
        if(!isVisible()) setVisible(true);
    }
    QLabel::setText(message);
}

// MyQLineEdit is a subclass used in this application
MyQLineEdit::MyQLineEdit(QWidget *parent,Fenim *fen,QString cod):QLineEdit(parent)
{
    Qmaitre = parent;
    Pfenim = (Fenim *)fen;
    Codeedit=cod;
    setFont(QFont("Arial",10,QFont::Normal));
}

void MyQLineEdit::keyPressEvent(QKeyEvent* e)
{
    Qt::KeyboardModifiers keyMod = QApplication::keyboardModifiers ();
    if(keyMod.testFlag(Qt::ControlModifier) && e->key() == 'A') Pfenim->SelectAllCalls();

    if(e->key()==Qt::Key_Down)
    {
        if(Codeedit=="cri") Pfenim->PFC[ESPECE]->LE->setFocus();
        else
        {
            for(int j=0;j<NBFIELDS;j++)
            {
                int ft = Pfenim->PFC[j]->FieldType;
                if(Codeedit==Pfenim->PFC[j]->FieldCode)
                {
                    if(ft==EC) Pfenim->PFC[j]->ECo->EcCo->setFocus();
                    else
                    {
                        if(j<NBFIELDS)
                        {
                            int ftb = Pfenim->PFC[j+1]->FieldType;

                            if(ftb==EC || ftb==SLI || ftb== SLE)
                                Pfenim->PFC[j+1]->LE->setFocus();
                        }
                    }
                }
            }
        }

    }
    if(e->key()==Qt::Key_Up)
    {
        if(Codeedit=="especes") Pfenim->PFenimWindow->EditCall->setFocus();
        else
        {
            for(int j=0;j<NBFIELDS;j++)
            {
                if(Codeedit==Pfenim->PFC[j]->FieldCode)
                {
                    if(j>0)
                    {
                        int ftb = Pfenim->PFC[j-1]->FieldType;
                        if(ftb==EC || ftb==SLI || ftb== SLE)
                            Pfenim->PFC[j-1]->LE->setFocus();
                    }
                }
            }
        }
    }
    QLineEdit::keyPressEvent(e);
}

// subclass of QComboBox
MyQComboBox::MyQComboBox(QWidget *parent,Fenim *fen,QString esp):QComboBox(parent)
{
    Qmaitre = parent;
    PFenim = fen;
    Codecombo=esp;
    setFont(QFont("Arial",10,QFont::Normal));
}

void MyQComboBox::keyPressEvent(QKeyEvent* e)
{
    if(PFenim!=0)
    {
        Qt::KeyboardModifiers keyMod = QApplication::keyboardModifiers ();
        if(keyMod.testFlag(Qt::ControlModifier) && e->key() == 'A') PFenim->SelectAllCalls();
    }
    QComboBox::keyPressEvent(e);
}

// Simple_LineEdit is an other subclass of MyQLineEdit which is not used by EditCombo class
Simple_LineEdit::Simple_LineEdit(QWidget *parent,Fenim *fen,QString cod):MyQLineEdit(parent,fen,cod)
{
    _pFenim=fen;
    connect(this,SIGNAL(textEdited(const QString&)),this,SLOT(UpdateText(const QString&)));
}

void Simple_LineEdit::UpdateText(const QString& s)
{
    this->setStyleSheet(_pFenim->InputColors[4]);
}

// EC_LineEdit is a subclass of MyQLineEdit used by EditCombo class
EC_LineEdit::EC_LineEdit(QWidget *parent,Fenim *fen,QString cod):MyQLineEdit(parent,fen,cod)
{
    _pFenim=fen;
    connect(this,SIGNAL(textEdited(const QString&)),this,SLOT(UpdateText(const QString&)));
}

void EC_LineEdit::SetEcp(EditCombo *pec)
{
    Ecp=pec;
}

// this method updates the QComboBox object when the text of the QLineEdit
// object is updated
void EC_LineEdit::UpdateText(const QString& s)
{
    Ecp->redoList(s);
    Ecp->EcLe->setStyleSheet(_pFenim->InputColors[4]);
}

void EC_LineEdit::keyPressEvent(QKeyEvent* e)
{
    if(e->key()==Qt::Key_Return)
    {
        QString sc = Ecp->EcCo->currentText();
        QString se = text();
        if(se.length()>0 && sc.length()>0 && sc.contains(se))
            Ecp->SelectCode(sc);
    }
    MyQLineEdit::keyPressEvent(e);
}

// EC_ComboBoxEdit is a subclass of MyQComboBoxEdit used by EditCombo class
EC_ComboBoxEdit::EC_ComboBoxEdit(QWidget *parent,Fenim *fen,QString cod):MyQComboBox(parent,fen,cod)
{
    connect(this, SIGNAL(activated(const QString&)), this, SLOT(SelectCode(const QString&)));
}

// this method updates the QLineEdit object when the text of the QComboBox
// object is updated
void EC_ComboBoxEdit::SelectCode(const QString& s)
{
    Ecp->SelectCode(s);
    Ecp->EcLe->setStyleSheet(PFenim->InputColors[4]);
}

void EC_ComboBoxEdit::keyPressEvent(QKeyEvent* e)
{
    if(e->key()==Qt::Key_Backspace || e->key()==Qt::Key_Delete)
    {
        Ecp->EcLe->setText("");
        Ecp->redoList("");
        showPopup();
    }
    if(e->key()==Qt::Key_Down)
    {
        this->showPopup();
    }
    if(e->key()==Qt::Key_Return)
    {
        Ecp->SelectCode(currentText());
    }
    MyQComboBox::keyPressEvent(e);
}

void EC_ComboBoxEdit::SetEcp(EditCombo *pec)
{
    Ecp=pec;
}

// EditCombo class is a class which associates a QComboBox object and a QLineEdit object
// and updates one when the other is modified
EditCombo::EditCombo(QWidget *parent,Fenim *fen,QString cod,QString englishCode,bool autaj)
{
    PFenimWindow = fen->PFenimWindow;
    EcLe=new EC_LineEdit(parent,fen,cod);
    EcCo=new EC_ComboBoxEdit(parent,fen,cod);
    EcLe->SetEcp(this);
    EcCo->SetEcp(this);
    CodeFi = cod;
    EnglishCode = englishCode;
    AllowAdd=autaj;
    ListCodes = new QStringList();
    QFile fichier;
    fichier.setFileName(cod+".txt");
    QTextStream textefi;
    if(fichier.open(QIODevice::ReadOnly)==true)
    {
        textefi.setDevice(&fichier);
        QString lte;
        bool trcod =  true;
        while(trcod)
        {
            if(textefi.atEnd()) trcod=false;
            else
            {
                lte = (textefi.readLine());
                if(lte.isNull()) trcod = false;
                else
                {
                    if(lte.isEmpty()) trcod = false;
                    else ListCodes->append(lte);
                }
            }
        }

    }
    redoList("");
}

// this method manages the list of choices according to entered text
void EditCombo::redoList(const QString& enteredText)
{
    EcCo->clear();
    if(enteredText.isEmpty()) EcCo->insertItems(0,*ListCodes);
    else
    {

        QStringList liste2;
        for(int i=0;i<ListCodes->size();i++)
        {
            if(ListCodes->at(i).contains(enteredText))
                liste2.append(ListCodes->at(i));
        }
        if(liste2.size()<1) EcCo->insertItems(0,*ListCodes);
        else EcCo->insertItems(0,liste2);
    }
}

// these methods manage the selection of a code in the QComboBox object
void EditCombo::SelectCode()
{
    if(EcCo->count()>0) SelectCode(EcCo->itemText(0));
}

void EditCombo::SelectCode(const QString& selectedText)
{
    if(EcCo->count()<1) EcCo->insertItems(0,*ListCodes);
    EcLe->setText(selectedText);
    EcLe->setFocus();
}

// this method processes the addition of a new code in a referential table
bool EditCombo::ConfirmAdd(QString& s)
{
    if(QMessageBox::question((QWidget *)PFenimWindow, (const QString &)QString("Question"),
                             //fr (const QString &)QString("Code ")+s+QString(" absent de la table : accepter ce code ?"),
                             (const QString &)QString("Code ")+s+QString(" code missing from the table : accept it ?"),
                             QMessageBox::Yes|QMessageBox::No)
            == QMessageBox::No) return(false);
    ListCodes->insert(0,s);
    ListCodes->sort();
    redoList(s);
    QFile fichier;
    QTextStream textefi;
    fichier.setFileName(CodeFi+".txt");
    if(fichier.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate))
    {
        textefi.setDevice(&fichier);
        for(int i=0;i<ListCodes->size();i++) textefi << ListCodes->at(i) << endl;
        fichier.close();
    }
    return(true);
}


// subclass of QPushButton
MyQPushButton::MyQPushButton(QWidget *parent):QPushButton(parent)
{
    QMaster = parent;
    setFont(QFont("Arial",10,QFont::Normal));
}

// subclass of QGraphicsView
MyQGraphicsView::MyQGraphicsView(QMainWindow *parent):QGraphicsView(parent)
{
    qmaitre = parent;
}

// method used to give information to the Loupe class object
MyQGraphicsView* Fenim::GetView()
{
    return(PFenimWindow->View);
}

// this method reads the version of the treated folder containing the treated file
bool Fenim::ReadFolderVersion()
{
    QString cbase = _wavFolder + _baseIniFile;
    FolderLogVersion = 0;
    FolderUserVersion = 0;
    if(!QFile::exists(cbase)) return(false);
    QSettings settings(_wavFolder + _baseIniFile, QSettings::IniFormat);
    settings.beginGroup("version");
    FolderLogVersion = settings.value("log").toInt();
    FolderUserVersion = settings.value("user").toInt();
    settings.endGroup();
    return(true);
}

// this method writes the version in the today folder of the reference database
// if it is new
void Fenim::WriteFolderVersion()
{
    QSettings settings(_dayBaseFolder.path() + _baseIniFile, QSettings::IniFormat);
    settings.beginGroup("version");
    settings.setValue("log", QVariant::fromValue(LogVersion));
    settings.setValue("user", QVariant::fromValue(UserVersion));
    settings.setValue("modeFreq", QVariant::fromValue(FrequencyType));
    settings.endGroup();
}
// ----------
// 15/03/2021
void Fenim::AffectLabel(int callNumber,QString species)
{
    EtiquetteArray[callNumber]->DataFields[ESPECE]=species;
}
// ----------
// 22/03/2021
bool Fenim::CreateDeepImage(int callNumber,QString species)
{
    bool xHalf;
    int imaWidth;
    LogStream << "cdi debut - callnumber=" << callNumber << endl;
    // SonogramWidth alimentee par loadCallsMatrices(...)
    if(SonogramWidth > 32767) {xHalf = true; imaWidth=(SonogramWidth+1)/2;}
    else  {xHalf = false; imaWidth=SonogramWidth;}
    //int lyi = qMin(PDetecTreatment->FftHeightHalf,PDetecTreatment->LimY);
    int lyi = ImageHeight; // bien verifier que c'est la bonne valeur que recupere loadcallsmatrices
    if(lyi != 128)
    {
        LogStream << "hauteur image # 128 : non gere pour l'instant !" << endl;
        return(false);
    }
    QImage ima = QImage(imaWidth, lyi,QImage::Format_RGB32);
    // $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    // chargement de l'image precedemment creee pour ne pas recreer tout et parce que dans le fichier .dat
    // on n'a pas toute l'information de SonogramArray mais seulement celle des cris
    ima.load(ImageFullName); // save image
    // $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    // mise en valeur du cri
    QVector<QPoint> unemat = ContoursMatrices.at(callNumber);
    int ycrimax = 0;
    int ycrimin = lyi;
    int xmin=6128,xmax=0;

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
    if(xmax-xmin < 9)
    {
        LogStream << "duree trop courte - image ima2 non enregistree !" << endl;
        return(false);
    }
    // $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    // mise en valeur du cri
    // mise en valeur du point maitre et des cretes
//
    LogStream << "cdi milieu" << callNumber << endl;

    //----
    // cretes :
    for(int jcrete=0;jcrete<3;jcrete++)
    {
        int ng = 80;
        if(jcrete==0) ng = 32;
        for(int j=0;j<CallsMatrix[jcrete][callNumber].size();j++)
        {
            int x=(int)(CallsMatrix[jcrete][callNumber][j].x()/(1+xHalf));
            int y=(int)(lyi-CallsMatrix[jcrete][callNumber][j].y()-1);
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
    QPoint p = this->MasterPointsVector.at(callNumber);
    int xmp=p.x(),ymp=p.y();
    // descendu le 1/6/2021 pour ympMin de *5 a *1
    int ympMin = (int)(PMainWindow->CoefSpe)*1;
    int ympMax = (int)(PMainWindow->CoefSpe)*50;
    if(ymp<=ympMin || ymp>ympMax)
    {
        LogStream << "frequence du point maitre hors limites ! ymp=" << ymp << endl;
        return(false);
    }
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
    for(int i=0;i<CallsNumber;i++)
    {
        if(i!= callNumber)
        {
            int ympc = MasterPointsVector[i].y();
            int xmpc = MasterPointsVector[i].x();
            bool afavoriser = false;
            if(ympc > ycrimin && ympc < ycrimax) afavoriser = true;
            QVector<QPoint> unemat = ContoursMatrices.at(i);
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

    if(xmp > imaWidth-5 || xmp <5)
    {
        LogStream << ImageFullName2 << " : point maitre trop pr�s des bords" << endl;
        return(false);
    }
    LogStream << "cdi proche fin" << callNumber << endl;

    QImage imac = ima.copy(xcd,0,xcf-xcd+1,lyi);

    // sauvegarde de l'image correspondant au cri callNumber
    QString imagePath2 = _wavFolder+"/ima2";
    QDir repima2(imagePath2);
    if(!repima2.exists()) repima2.mkdir(imagePath2);

    //QString callIma2Name = imagePath2 + "/" + _mainFileName + "--" + QString::number(callNumber) + ".jpg";
    if(PMainWindow->MultipleSounds == 1) EndName = EndsNames[callNumber];

    QString callIma2Name = imagePath2 + "/" + species + "--" + _mainFileName + EndName;
    LogStream << "callIma2Name=" << callIma2Name << endl;
    imac.save(callIma2Name,0,100); // save image
    return(true);
}


bool Fenim::readDeepMode(QString dirpath)
{
    return(QFile::exists(dirpath + "/deepmode.txt"));
}

int Fenim::SortCallsArrays()
{
    sortArrays(Intensites,CallsNumber,NCRISSEL,CrisLesPlusForts);
    sortArrays(Durees,CallsNumber,NCRISSEL,CrisLesPlusLongs);
    int nsel = 0;
    int *queltab;
    for(int i=0;i<2;i++)
    {
        if(i==0) queltab = CrisLesPlusForts; else queltab = CrisLesPlusLongs;
        for(int j=0;j<NCRISSEL;j++)
        {
            if(queltab[j] < 0) continue;
            bool onpeutprendre = true;
            if(nsel>0)
            {
                for(int l=0;l<nsel;l++)
                {
                    if(CrisSel[l]==queltab[j]) {onpeutprendre = false; break;}
                }
            }
            if(onpeutprendre)
            {
                CrisSel[nsel] = queltab[j];
                nsel++;
            }
        }
    }
    return(nsel);
}

void Fenim::sortArrays(int *pf,int nbf,int ncla,int *cla)
{
    for(int j=0;j<ncla;j++)
    {
        int lemeilleur = -1;
        int meilleurscore = -1;
        for(int k=0;k<nbf;k++)
        {
            bool onpeutprendre = true;
            if(j>0)
            {
                for(int l=0;l<j;l++)
                {
                    if(cla[l]==k) {onpeutprendre = false; break;}
                }
            }
            if(onpeutprendre)
            {
                if(pf[k] > meilleurscore)
                {
                    meilleurscore = pf[k];
                    lemeilleur = k;
                }
            }
        }
        if(lemeilleur > -1) cla[j] = lemeilleur;
    }
}


