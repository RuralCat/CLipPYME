#!/usr/bin/python

##################
# smimainframe.py
#
# Copyright David Baddeley, 2009
# d.baddeley@auckland.ac.nz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################
''' 
This contains the bulk of the GUI code for the main window of PYMEAcquire.
'''


import wx
import wx.py.shell

import PYME.misc.autoFoldPanel as afp
#from PYME.misc.fbpIcons import *

import sys
import os
#sys.path.append('.')
import logging
logging.basicConfig(level=logging.DEBUG)

import wx.lib.agw.aui as aui

#import PYME.cSMI as example
import PYME.DSView.displaySettingsPanel as disppanel
from PYME.DSView import arrayViewPanel

from PYME.Acquire import mytimer
from PYME.Acquire import psliders
from PYME.Acquire import intsliders
from PYME.Acquire import seqdialog
#from PYME.Acquire import timeseqdialog
from PYME.Acquire import stepDialog
from PYME.Acquire import selectCameraPanel
from PYME.Acquire import microscope
#import PYME.DSView.dsviewer_npy as dsviewer
from PYME.DSView import dsviewer_npy_nb as dsviewer
#from PYME.cSMI import CDataStack_AsArray
from PYME.Acquire import MetaDataHandler
#from PYME.Acquire import chanfr
from PYME.Acquire import HDFSpoolFrame
from PYME.FileUtils import nameUtils

from PYME.Acquire import splashScreen
import time

import PYME.Acquire.protocol as protocol

def create(parent, options = None):
    return PYMEMainFrame(parent, options)

[wxID_SMIMAINFRAME, wxID_SMIMAINFRAMENOTEBOOK1, wxID_SMIMAINFRAMEPANEL1, 
 wxID_SMIMAINFRAMESTATUSBAR1, wxID_SMIMAINFRAMETEXTCTRL1, 
] = [wx.NewId() for i in range(5)]

[wxID_SMIMAINFRAMEMENU1FILE_EXIT, wxID_SMIMAINFRAMEMENU1FILE_OPEN, 
 wxID_SMIMAINFRAMEMENU1FILE_OPEN_SCRIPT, 
] = [wx.NewId() for i in range(3)]

[wxID_SMIMAINFRAMEMFILEFILE_EXIT, wxID_SMIMAINFRAMEMFILEFILE_OPEN, 
] =[wx.NewId() for i in range(2)]

[wxID_SMIMAINFRAMEWINDOWSITEMS0] = [wx.NewId() for i in range(1)]

[wxID_SMIMAINFRAMEMAQUIREONE_PIC, wxID_SMIMAINFRAMEMAQUIRESTACK, 
 wxID_SMIMAINFRAMEMAQUIRETD_SERIES, wxID_SMIMAINFRAMEMAQUIRETWO_D_TIME, 
] = [wx.NewId() for i in range(4)]

[wxID_SMIMAINFRAMEMCONTROLSCAM, wxID_SMIMAINFRAMEMCONTROLSINT_TIME, 
 wxID_SMIMAINFRAMEMCONTROLSPIEZO, wxID_SMIMAINFRAMEMCONTROLSPIEZO_INIT, 
 wxID_SMIMAINFRAMEMCONTROLSSTEP, 
] = [wx.NewId() for i in range(5)]

[wxID_SMIMAINFRAMEMCAMBIN, wxID_SMIMAINFRAMEMCAMCHANS, 
 wxID_SMIMAINFRAMEMCAMROI, 
] = [wx.NewId() for i in range(3)]

[wxID_SMIMAINFRAMEMDISPLAYCLEAR_SEL] = [wx.NewId()]

class PYMEMainFrame(wx.Frame):
    '''The main window class'''
    def _init_coll_mCam_Items(self, parent):
        # generated method, don't edit

        parent.Append(wxID_SMIMAINFRAMEMCAMROI,
              'Set ROI\tF8', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_SMIMAINFRAMEMCAMBIN,
              'Turn Binning on', kind=wx.ITEM_CHECK)
        parent.Append(wxID_SMIMAINFRAMEMCAMCHANS,
              'Channels', kind=wx.ITEM_NORMAL)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMCAMBIN, self.OnMCamBin)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMCAMCHANS, self.OnMCamChans)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMCAMROI, self.OnMCamRoi)

        parent.AppendSeparator()
        ID_SETVOXELSIZE = wx.NewId()
        parent.Append(ID_SETVOXELSIZE, 'Set Pixel Size')
        wx.EVT_MENU(self, ID_SETVOXELSIZE, self.OnMCamSetPixelSize)

    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.mFile, title='&File')
        parent.Append(menu=self.mControls, title='&Controls')
        parent.Append(menu=self.mAquire, title='&Aquire')

    def _init_coll_mDisplay_Items(self, parent):
        # generated method, don't edit

        parent.Append(wxID_SMIMAINFRAMEMDISPLAYCLEAR_SEL,
              'Clear Selection', kind=wx.ITEM_NORMAL)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMDISPLAYCLEAR_SEL,
              self.OnMDisplayClearSel)

    def _init_coll_mFile_Items(self, parent):
        # generated method, don't edit

        parent.Append(wxID_SMIMAINFRAMEMFILEFILE_OPEN,
              '&Open Stack', kind=wx.ITEM_NORMAL)
        parent.AppendSeparator()
        parent.Append(wxID_SMIMAINFRAMEMFILEFILE_EXIT,
              'E&xit', kind=wx.ITEM_NORMAL)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMFILEFILE_OPEN, self.OnFileOpenStack)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMFILEFILE_EXIT, self.OnFileExit)

    def _init_coll_mControls_Items(self, parent):
        # generated method, don't edit

        parent.Append(wxID_SMIMAINFRAMEMCONTROLSINT_TIME,
              'Integration Time', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_SMIMAINFRAMEMCONTROLSPIEZO,
              'Piezos', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_SMIMAINFRAMEMCONTROLSSTEP,
              'Stepper Motors', kind=wx.ITEM_NORMAL)
        #parent.AppendMenu( id=wxID_SMIMAINFRAMEMCONTROLSCAM,
        #      string='Camera', subMenu=self.mCam)
        parent.AppendSubMenu(self.mCam, 'Camera')
        parent.AppendSeparator()
        parent.Append(wxID_SMIMAINFRAMEMCONTROLSPIEZO_INIT,
              'Piezo Init', kind=wx.ITEM_NORMAL)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMCONTROLSINT_TIME, self.OnMIntTime)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMCONTROLSPIEZO, self.OnMPiezo)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMCONTROLSSTEP, self.OnMStep)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMCONTROLSPIEZO_INIT,
              self.OnMControlsPiezoInit)



    def _init_coll_mAquire_Items(self, parent):
        # generated method, don't edit

        parent.Append(wxID_SMIMAINFRAMEMAQUIREONE_PIC,
              '1 Pic\tF5', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_SMIMAINFRAMEMAQUIRESTACK,
              '3D Stack', kind=wx.ITEM_NORMAL)
        parent.AppendSeparator()
        parent.Append(wxID_SMIMAINFRAMEMAQUIRETWO_D_TIME,
              'Time Series [2D]', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_SMIMAINFRAMEMAQUIRETD_SERIES,
              'Time Series [3D]', kind=wx.ITEM_NORMAL)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMAQUIRESTACK, self.OnMAquireStack)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMAQUIREONE_PIC, self.OnMAquireOnePic)
        wx.EVT_MENU(self, wxID_SMIMAINFRAMEMAQUIRETWO_D_TIME,self.OnMAquireTwo_d_timeMenu)

    def _init_utils(self):
        # generated method, don't edit
        self.menuBar1 = wx.MenuBar()

        self.mFile = wx.Menu(title='')

        self.mControls = wx.Menu(title='')

        self.mAquire = wx.Menu(title='')

        self.mCam = wx.Menu(title='')

        self.mDisplay = wx.Menu(title='')

        self._init_coll_menuBar1_Menus(self.menuBar1)
        self._init_coll_mFile_Items(self.mFile)
        self._init_coll_mControls_Items(self.mControls)
        self._init_coll_mAquire_Items(self.mAquire)
        self._init_coll_mCam_Items(self.mCam)
        self._init_coll_mDisplay_Items(self.mDisplay)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_SMIMAINFRAME, name='smiMainFrame',
              parent=prnt, pos=wx.Point(20, 20), size=wx.Size(600, 800),
              style=wx.DEFAULT_FRAME_STYLE, title='PYME Acquire in Lab')
        self._init_utils()
        self.SetClientSize(wx.Size(1020, 800))
        self.SetMenuBar(self.menuBar1)

        self.statusBar1 = wx.StatusBar(id=wxID_SMIMAINFRAMESTATUSBAR1,
              name='statusBar1', parent=self, style=wx.ST_SIZEGRIP)
        self.SetStatusBar(self.statusBar1)

        #self.notebook1 = wx.Notebook(id=wxID_SMIMAINFRAMENOTEBOOK1,
        #      name='notebook1', parent=self, pos=wx.Point(0, 0), size=wx.Size(618,
        #      450), style=0)
        #self.notebook1 = wx.aui.AuiNotebook(id=wxID_SMIMAINFRAMENOTEBOOK1, parent=self, pos=wx.Point(0, 0), size=wx.Size(618,
        #      450), style=wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_TAB_SPLIT)

        ##self.notebook1 = AuiNotebookWithFloatingPages(id=wxID_SMIMAINFRAMENOTEBOOK1, parent=self, pos=wx.Point(0, 0), size=wx.Size(1000,
        ##      -1), style=wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_TAB_SPLIT)

#        self.panel1 = wx.Panel(id=wxID_SMIMAINFRAMEPANEL1, name='panel1',
#              parent=self.notebook1, pos=wx.Point(0, 0), size=wx.Size(-1, -1),
#              style=wx.TAB_TRAVERSAL)
#
#        self.textCtrl1 = wx.TextCtrl(id=wxID_SMIMAINFRAMETEXTCTRL1,
#              name='textCtrl1', parent=self.panel1, pos=wx.Point(121, 56),
#              size=wx.Size(368, 312), style=0,
#              value='PySMI    Version 0.5   KIP Heidelberg')
#        self.textCtrl1.Enable(False)
#        self.textCtrl1.Center(wx.BOTH)

    def __init__(self, parent, options = None):
        self._init_ctrls(parent)
        self.options = options

        self._mgr = aui.AuiManager(agwFlags = aui.AUI_MGR_DEFAULT | aui.AUI_MGR_AUTONB_NO_CAPTION)

        atabstyle = self._mgr.GetAutoNotebookStyle()
        self._mgr.SetAutoNotebookStyle((atabstyle ^ aui.AUI_NB_BOTTOM) | aui.AUI_NB_TOP)

        # tell AuiManager to manage this frame
        self._mgr.SetManagedWindow(self)

        self.snapNum = 0

        

        wx.EVT_CLOSE(self, self.OnCloseWindow)        
        
        self.MainFrame = self #reference to this window for use in scripts etc...
        self.MainMenu = self.menuBar1
        protocol.MainFrame = self

        self.toolPanels = []
        self.camPanels = []
        self.postInit = []

        self.initDone = False

        self.scope = microscope.microscope()

        self.splash = splashScreen.SplashScreen(self, self.scope)
        self.splash.Show()
        

#        self.sh = wx.py.shell.Shell(id=-1,
#              parent=self.notebook1, size=wx.Size(-1, -1), style=0, locals=self.__dict__,
#              introText='Python SMI bindings - note that help, license etc below is for Python, not PySMI\n\n')
#
        self.sh = wx.py.shell.Shell(id=-1,
              parent=self, size=wx.Size(-1, -1), style=0, locals=self.__dict__,
              introText='Python SMI bindings - note that help, license etc below is for Python, not PySMI\n\n')

        
        #self.notebook1.AddPage(imageId=-1, page=self.sh, select=True, text='Console')
        #self.notebook1.AddPage(imageId=-1, page=self.panel1, select=False, text='About')
        
        #self.notebook1.AddPage(page=self.sh, select=True, caption='Console')
        self._mgr.AddPane(self.sh, aui.AuiPaneInfo().
                          Name("shell").Caption("Console").Centre().CloseButton(False))
#        self.notebook1.AddPage( page=self.panel1, select=False, caption='About')

        #self.SetSize((400, 800))
        self.CreateToolPanel()
        #self.SetSize((1000, 800))
        
        
        #self.sizer = wx.BoxSizer()
        #self.sizer.Add(self.notebook1, 1, wx.EXPAND)
        #self.SetSizer(self.Sizer)
        self.SetSize((1030, 895))
        #self._mgr.Update()
        
        self.roi_on = False
        self.bin_on = False
        
        self.time1 = mytimer.mytimer()
        
        self.time1.Start(500)

        self.time1.WantNotification.append(self.runInitScript)
        self.time1.WantNotification.append(self.checkInitDone)
        self.time1.WantNotification.append(self.splash.Tick)

    def AddPage(self, page=None, select=True,caption='Dummy'):
        '''Add a page to the main notebook
        
        Parameters
        ----------
        page : an instance of a wx.Window derived class
            The page to add
        select : bool
            Whether to give the page focus after adding it
        caption : string
            The caption for the page.
        '''
        pn = self._mgr.GetPaneByName("shell")
        if pn.IsNotebookPage():
            #nb = self._mgr.GetNotebooks()[pn.notebook_id]
            #currPage = nb.GetSelection()
            #print currPage
            self._mgr.AddPane(page, aui.AuiPaneInfo().
                          Name(caption.replace(' ', '')).Caption(caption).CloseButton(False).NotebookPage(pn.notebook_id))
            #if not select:
            #    nb.SetSelection(currPage)
        else:
            self._mgr.AddPane(page, aui.AuiPaneInfo().
                          Name(caption.replace(' ', '')).Caption(caption).CloseButton(False), target=pn)

        #self._mgr.Update()
        #self._mgr.AddPane(page, aui.AuiPaneInfo().
        #                  Name(caption.replace(' ', '')).Caption(caption).CloseButton(False).Float())

    def runInitScript(self):
        #import os
        self.time1.WantNotification.remove(self.runInitScript)
        #self.sh.shell.runfile('init.py')
        #fstub = os.path.join(os.path.split(__file__)[0], 'Scripts')
        initFile = 'init.py'
        if not self.options == None and not self.options.initFile == None:
            initFile = self.options.initFile
            
        #initFile = os.path.join(fstub, initFile)
        self.sh.run('from PYME.Acquire import ExecTools')
        self.sh.run('ExecTools.setDefaultNamespace(locals(), globals())')
        self.sh.run('from PYME.Acquire.ExecTools import InitBG, joinBGInit, InitGUI, HWNotPresent')
        #self.sh.run('''def InitGUI(code):\n\tpostInit.append(code)\n\n\n''')
        self.sh.run('ExecTools.execFileBG("%s", locals(), globals())' % initFile)

        

    def checkInitDone(self):
        if self.scope.initDone == True and self.checkInitDone in self.time1.WantNotification:
            self.time1.WantNotification.remove(self.checkInitDone)
            #self.time1.WantNotification.remove(self.splash.Tick)
            self.doPostInit()
    
    def _refreshDataStack(self):
        if 'vp' in dir(self):
            self.vp.SetDataStack(self.scope.pa.dsa)
        
    def livepreview(self):
        self.scope.startAquisistion()

        if self.scope.cam.GetPicHeight() > 1:
            if 'vp' in dir(self):
                self.vp.SetDataStack(self.scope.pa.dsa)
            else:
                self.vp = arrayViewPanel.ArrayViewPanel(self, self.scope.pa.dsa)
                self.vp.crosshairs = False
                self.vp.showScaleBar = False
                self.vp.do.leftButtonAction = self.vp.do.ACTION_SELECTION
                self.vp.do.showSelection = True
                self.vp.CenteringHandlers.append(self.scope.centreView)

                self.vsp = disppanel.dispSettingsPanel2(self, self.vp)


                self.time1.WantNotification.append(self.vsp.RefrData)

                self.AddPage(page=self.vp, select=True,caption='Preview')

                self.AddCamTool(self.vsp, 'Display')

            self.scope.pa.WantFrameGroupNotification.append(self.vp.Redraw)

        else:
            #1d data - use graph instead
            from PYME.Analysis.LMVis import fastGraph
            if 'sp' in dir(self):
                    pass
            else:
                self.sp = fastGraph.SpecGraphPanel(self, self)

                self.AddPage(page=self.sp, select=True,caption='Preview')

            self.scope.pa.WantFrameGroupNotification.append(self.sp.refr)
            
        self.scope.PACallbacks.append(self._refreshDataStack)


    def doPostInit(self):
        logging.debug('Starting post-init')
        for cm in self.postInit:
            #print cm
            for cl in cm.split('\n'):
                self.sh.run(cl)

        if len(self.scope.piezos) > 0.5:
            self.piezo_sl = psliders.PiezoSliders(self.scope.piezos, self, self.scope.joystick)
            self.time1.WantNotification.append(self.piezo_sl.update)

            self.AddTool(self.piezo_sl, 'Positioning')

            #self.notebook1.AddPage( page=self.piezo_sl, select=False, caption='Piezo Control')
            #self.notebook1.Split(self.notebook1.GetPageCount() -1, wx.DOWN)
            #self.piezo_sl.Show()

            #self.time1.WantNotification.append(self.piezo_sl.update)

            self.seq_d = seqdialog.seqPanel(self, self.scope)
            self.AddAqTool(self.seq_d, 'Z-Stack')
            #self.seq_d.Show()

        if (self.scope.cam.CamReady() and ('chaninfo' in self.scope.__dict__)):
            self.livepreview()
            

            self.int_sl = intsliders.IntegrationSliders(self.scope.chaninfo,self, self.scope)
            self.AddCamTool(self.int_sl, 'Integration Time')
            #self.notebook1.AddPage( page=self.int_sl, select=False, caption='Integration Time')
            #self.notebook1.Split(self.notebook1.GetPageCount() -1, wx.DOWN)
            #self.int_sl.Show()

            if len(self.scope.cameras) > 1:
                self.pCamChoose = selectCameraPanel.CameraChooserPanel(self, self.scope)
                self.AddCamTool(self.pCamChoose, 'Camera Selection')

            #self.tseq_d = timeseqdialog.seqDialog(self, self.scope)

            self.pan_spool = HDFSpoolFrame.PanSpool(self, self.scope, nameUtils.genHDFDataFilepath())
            
            self.AddAqTool(self.pan_spool, 'Spooling')

        
            
        if 'step' in self.scope.__dict__:
            self.step_d = stepDialog.stepPanel(self, self.scope)
            #self.step_d.Show()
            self.AddTool(self.step_d, 'Stepper Motors')
        
        self.time1.WantNotification.append(self.StatusBarUpdate)

        for t in self.toolPanels:
            print(t)
            self.AddTool(*t)

        for t in self.camPanels:
            print(t)
            self.AddCamTool(*t)

        #self.splash.Destroy()

        
        
        self.initDone = True
        self._mgr.Update()

        if 'pCamChoose' in dir(self):
            self.pCamChoose.OnCCamera(None)
            
        logging.debug('Finished post-init')

        #fudge to get layout right
#        panes = self.notebook1.GetAuiManager().AllPanes
#
#        self.paneNames = []
#
#        for p in panes:
#            self.paneNames.append(p.name)

        #self.LoadPerspective()

    def _getPerspectiveFilename(self):
        #print __file__
        fname = os.path.join(os.path.split(__file__)[0], 'GUILayout.txt')
        return fname

    def SavePerspective(self):
        #mgr = self.notebook1.GetAuiManager()
        persp = self._mgr.SavePerspective()

        for i, p in enumerate(self.paneNames):
            persp = persp.replace(p, 'pane_%d' % i)
            
        f = open(self._getPerspectiveFilename(), 'w')
        f.write(persp)
        f.close()

    def LoadPerspective(self):
        pfname = self._getPerspectiveFilename()
        if os.path.exists(pfname):
            f = open(pfname)
            persp = f.read()
            f.close()

            for i, p in enumerate(self.paneNames):
                persp = persp.replace('pane_%d' % i, p)

            self._mgr.LoadPerspective(persp)
            self._mgr.Update()


    def CreateToolPanel(self):
        self.camPanel = afp.foldPanel(self, -1, wx.DefaultPosition,
                                     wx.Size(240,1000))

        cpinfo = aui.AuiPaneInfo().Name("camControls").Caption("Camera").Layer(1).Right().CloseButton(False)
        #cpinfo.dock_proportion  = int(cpinfo.dock_proportion*1.6)
        
        self._mgr.AddPane(self.camPanel, cpinfo)

        ##############################################################3

        self.aqPanel = afp.foldPanel(self, -1, wx.DefaultPosition,
                                     wx.Size(240,1500))

        aqinfo = aui.AuiPaneInfo().Name("aqControls").Caption("Acquisition").Layer(2).Position(0).Right().CloseButton(False).BestSize(240, 1500)
        
        self._mgr.AddPane(self.aqPanel, aqinfo)

        self.toolPanel = afp.foldPanel(self, -1, wx.DefaultPosition,
                                     wx.Size(240,-1))
#        self.toolPanel = fpb.FoldPanelBar(self, -1, wx.DefaultPosition,
#                                     wx.Size(240,200))#, fpb.FPB_DEFAULT_STYLE,0)

        self._mgr.AddPane(self.toolPanel, aui.AuiPaneInfo().
                          Name("hardwareControls").Caption("Hardware").Layer(2).Position(1).Right().CloseButton(False))
                          #Name("hardwareControls").Caption("Hardware").Layer(2).Position(1).Right().CloseButton(False).BestSize(240, 50))

        #s416-spool
        #aqinfo.dock_proportion  = int(aqinfo.dock_proportion*1.3)
        aqinfo.dock_proportion  = int(aqinfo.dock_proportion*4)



    def AddTool(self, panel, title):
        '''Adds a pane to the tools section of the GUI
        
        Parameters
        ----------
        panel : an instance of a wx.Window derived class
            The pane to add
        title : string
            The caption for the panel.
        '''
        item = afp.foldingPane(self.toolPanel, -1, caption=title, pinned = True)
        panel.Reparent(item)
        item.AddNewElement(panel)
        self.toolPanel.AddPane(item)
#        item = self.toolPanel.AddFoldPanel(title, collapsed=False, foldIcons=self.Images)
#        panel.Reparent(item)
#        self.toolPanel.AddFoldPanelWindow(item, panel, fpb.FPB_ALIGN_WIDTH, fpb.FPB_DEFAULT_SPACING, 10)
        #wx.LayoutAlgorithm().LayoutWindow(self, self._leftWindow1)

    def AddCamTool(self, panel, title):
        '''Adds a pane to the Camera section of the GUI
        
        Parameters
        ----------
        panel : an instance of a wx.Window derived class
            The pane to add
        title : string
            The caption for the panel.
        '''
        #item = self.camPanel.AddFoldPanel(title, collapsed=False, foldIcons=self.Images)
        item = afp.foldingPane(self.camPanel, -1, caption=title, pinned = True)
        panel.Reparent(item)
        item.AddNewElement(panel)
        self.camPanel.AddPane(item)
        #self.camPanel.AddFoldPanelWindow(item, panel, fpb.FPB_ALIGN_WIDTH, fpb.FPB_DEFAULT_SPACING, 10)

    def AddAqTool(self, panel, title):
        '''Adds a pane to the Acquisition section of the GUI
        
        Parameters
        ----------
        panel : an instance of a wx.Window derived class
            The pane to add
        title : string
            The caption for the panel.
        '''
        item = afp.foldingPane(self.aqPanel, -1, caption=title, pinned = True)
        panel.Reparent(item)
        item.AddNewElement(panel)
        self.aqPanel.AddPane(item)
        #item = self.aqPanel.AddFoldPanel(title, collapsed=False, foldIcons=self.Images)
        #panel.Reparent(item)
        #self.aqPanel.AddFoldPanelWindow(item, panel, fpb.FPB_ALIGN_WIDTH, fpb.FPB_DEFAULT_SPACING, 10)
        #wx.LayoutAlgorithm().LayoutWindow(self, self._leftWindow1)

    def OnFileOpenStack(self, event):
        #self.dv = dsviewer.DSViewFrame(self)
        #self.dv.Show()
        im = dsviewer.ImageStack()
        dvf = dsviewer.DSViewFrame(im, parent=self, size=(500, 500))
        dvf.SetSize((500,500))
        dvf.Show()
        event.Skip()

    def OnFileExit(self, event):
        self.Close()
        #event.Skip()
        
    def StatusBarUpdate(self):
        self.statusBar1.SetStatusText(self.scope.genStatus())

    def OnMAquireStack(self, event):
        self.seq_d.Show()
        self.seq_d.Raise()
        #event.Skip()

    def OnMAquireOnePic(self, event):
        import numpy as np
        self.scope.pa.stop()
        ds2 = np.atleast_3d(self.scope.pa.dsa.reshape(self.scope.cam.GetPicWidth(),self.scope.cam.GetPicHeight()).copy())


        #metadata handling
        mdh = MetaDataHandler.NestedClassMDHandler()
        mdh.setEntry('StartTime', time.time())
        mdh.setEntry('AcquisitionType', 'SingleImage')

        #loop over all providers of metadata
        for mdgen in MetaDataHandler.provideStartMetadata:
            mdgen(mdh)

        im = dsviewer.ImageStack(data = ds2, mdh = mdh, titleStub='Unsaved Image')
        if not im.mode == 'graph':
            im.mode = 'lite'

        #print im.mode
        dvf = dsviewer.DSViewFrame(im, mode= im.mode, size=(500, 500))
        dvf.SetSize((500,500))
        dvf.Show()

        self.snapNum += 1

        self.scope.pa.Prepare(True)
        self.scope.pa.start()

        #event.Skip()

    def OnMIntTime(self, event):
        self.int_sl.Show()
        self.int_sl.Raise()
        #event.Skip()

    def OnMPiezo(self, event):
        self.piezo_sl.Show()
        self.piezo_sl.Raise()
        #event.Skip()

    def OnMStep(self, event):
        self.step_d.Show()
        self.step_d.Raise()
        #event.Skip()

    def OnMCamBin(self, event):
        self.scope.pa.stop()
        if (self.bin_on):
            self.scope.cam.SetHorizBin(1)
            self.scope.cam.SetVertBin(1)
            self.mCam.SetLabel(wxID_SMIMAINFRAMEMCAMBIN, 'Turn Binning On')
            self.bin_on = False
        else:
            self.scope.cam.SetHorizBin(16)
            self.scope.cam.SetVertBin(16)
            self.mCam.SetLabel(wxID_SMIMAINFRAMEMCAMBIN, 'Turn Binning Off')
            self.bin_on = True
            
        self.scope.cam.SetCOC()
        self.scope.cam.GetStatus()
        self.scope.pa.Prepare()
        self.scope.vp.SetDataStack(self.scope.pa.dsa)
        self.scope.pa.start()
        #event.Skip()

    def OnMCamSetPixelSize(self, event):
        from PYME.Acquire import voxelSizeDialog

        dlg = voxelSizeDialog.VoxelSizeDialog(self, self.scope)
        dlg.ShowModal()

    def OnMCamChans(self, event):
        #return
        self.scope.pa.stop()
        
        chand = chanfr.ChanFrame(self, self.scope.chaninfo)
        chand.ShowModal()
        
        self.int_sl.Destroy()
        self.int_sl = intsliders.IntegrationSliders(self.scope.chaninfo,self)
        self.int_sl.Show()
            
        self.scope.pa.Prepare()
        self.scope.vp.SetDataStack(self.scope.pa.dsa)
        self.scope.pa.start()
        #event.Skip()

    def OnMCamRoi(self, event):
        self.scope.pa.stop()
        
        #print (self.scope.vp.selection_begin_x, self.scope.vp.selection_begin_y, self.scope.vp.selection_end_x, self.scope.vp.selection_end_y)

        if 'validROIS' in dir(self.scope.cam):
            #special case for cameras with restricted ROIs - eg Neo
            print('setting ROI')
            dlg = wx.SingleChoiceDialog(self, 'Please select the ROI size', 'Camera ROI', ['%dx%d at (%d, %d)' % roi for roi in self.scope.cam.validROIS])
            dlg.ShowModal()
            print('Dlg Shown')
            self.scope.cam.SetROIIndex(dlg.GetSelection())
            dlg.Destroy()
            
            x1 = 0
            y1 = 0
            x2 = self.scope.cam.GetPicWidth()
            y2 = self.scope.cam.GetPicHeight()
            print ('ROI Set')
        
        else:
            if (self.roi_on):
                x1 = self.scope.cam.GetROIX1()
                y1 = self.scope.cam.GetROIY1()
                x2 = self.scope.cam.GetROIX2()
                y2 = self.scope.cam.GetROIY2()
    
                self.scope.cam.SetROI(0,0, self.scope.cam.GetCCDWidth(), self.scope.cam.GetCCDHeight())
                self.mCam.SetLabel(wxID_SMIMAINFRAMEMCAMROI, 'Set ROI\tF8')
                self.roi_on = False
            else:
                #x1 = self.scope.vp.selection_begin_x
                #y1 = self.scope.vp.selection_begin_y
                #x2 = self.scope.vp.selection_end_x
                #y2 = self.scope.vp.selection_end_y
    
                x1, y1, x2, y2 = self.scope.vp.do.GetSliceSelection()
    
                #if we're splitting colours/focal planes across the ccd, then only allow symetric ROIs
                if 'splitting' in dir(self.scope.cam):
                    if self.scope.cam.splitting.lower() == 'left_right':
                        x1 = min(x1, self.scope.cam.GetCCDWidth() - x2)
                        x2 = max(x2, self.scope.cam.GetCCDWidth() - x1)
                    if self.scope.cam.splitting.lower() == 'up_down':
                        y1 = min(y1, self.scope.cam.GetCCDHeight() - y2)
                        y2 = max(y2, self.scope.cam.GetCCDHeight() - y1)
    
                        if not self.scope.cam.splitterFlip:
                            y1 = 0
                            y2 = self.scope.cam.GetCCDHeight()
                        
                self.scope.cam.SetROI(x1,y1,x2,y2)
                self.mCam.SetLabel(wxID_SMIMAINFRAMEMCAMROI, 'Clear ROI\tF8')
                self.roi_on = True
    
                x1 = 0
                y1 = 0
                x2 = self.scope.cam.GetPicWidth()
                y2 = self.scope.cam.GetPicHeight()

            
        print('about to set COC')
        self.scope.cam.SetCOC()
        self.scope.cam.GetStatus()
        self.scope.pa.Prepare()
        self.scope.vp.SetDataStack(self.scope.pa.dsa)
        
        #self.scope.vp.selection_begin_x = x1
        #self.scope.vp.selection_begin_y = y1
        #self.scope.vp.selection_end_x = x2
        #self.scope.vp.selection_end_y = y2
        self.scope.vp.do.SetSelection((x1,y1,0), (x2,y2,0))

        self.scope.pa.start()
        self.scope.vp.Refresh()
        self.scope.vp.GetParent().Refresh()
        #event.Skip()

    def SetCentredRoi(self, event=None, halfwidth=5):
        self.scope.pa.stop()

        #print (self.scope.vp.selection_begin_x, self.scope.vp.selection_begin_y, self.scope.vp.selection_end_x, self.scope.vp.selection_end_y)

        w = self.scope.cam.GetCCDWidth()
        h = self.scope.cam.GetCCDHeight()

        x1 = w/2 - halfwidth
        y1 = h/2 - halfwidth
        x2 = w/2 + halfwidth
        y2 = h/2 + halfwidth

        self.scope.cam.SetROI(x1,y1,x2,y2)
        self.mCam.SetLabel(wxID_SMIMAINFRAMEMCAMROI, 'Clear ROI\tF8')
        self.roi_on = True

        x1 = 0
        y1 = 0
        x2 = self.scope.cam.GetPicWidth()
        y2 = self.scope.cam.GetPicHeight()


        self.scope.cam.SetCOC()
        self.scope.cam.GetStatus()
        self.scope.pa.Prepare()
        self.scope.vp.SetDataStack(self.scope.pa.dsa)

        self.scope.vp.selection_begin_x = x1
        self.scope.vp.selection_begin_y = y1
        self.scope.vp.selection_end_x = x2
        self.scope.vp.selection_end_y = y2

        self.scope.pa.start()
        self.scope.vp.Refresh()
        self.scope.vp.GetParent().Refresh()
        #event.Skip()

    def OnMDisplayClearSel(self, event):
        self.vp.ResetSelection()
        #event.Skip()

    def OnMControlsPiezoInit(self, event):
        self.scope.pz.Init(1)
        self.piezo_sl.update()
        #event.Skip()

    def OnMAquireTwo_d_timeMenu(self, event):
        self.tseq_d.Show()
        self.tseq_d.Raise()
        #event.Skip()

    def OnCloseWindow(self, event):   
        self.scope.pa.stop()
        self.time1.Stop()
        if 'cameras' in dir(self.scope):
            for c in self.scope.cameras.values():
                c.Shutdown()
        else:
            self.scope.cam.Shutdown()
        for f in self.scope.CleanupFunctions:
            f()
            
        print 'All cleanup functions called'
        
        time.sleep(1)
        
        import threading
        print 'Remaining Threads:'
        for t in threading.enumerate():
            print t, t._Thread__target
        #self.int_sl.Destroy()
        #self.piezo_sl.Destroy()
        #self.seq_d.Destroy()
        #self.Close()
        self.Destroy()
        wx.Exit()
        
