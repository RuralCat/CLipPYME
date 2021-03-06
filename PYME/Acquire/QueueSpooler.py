#!/usr/bin/python

##################
# QueueSpooler.py
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

import tables
from PYME.Acquire import MetaDataHandler
#from PYME import cSMI
import Pyro.core
import os
import time

import PYME.Acquire.Spooler as sp
from PYME.Acquire import protocol as p
from PYME.FileUtils import fileID

#rom PYME.Acquire import eventLog

class SpoolEvent(tables.IsDescription):
   EventName = tables.StringCol(32)
   Time = tables.Time64Col()
   EventDescr = tables.StringCol(256)

class EventLogger:
   def __init__(self, spool, scope, tq, queueName):
      self.spooler = spool
      self.scope = scope
      self.tq = tq
      self.queueName = queueName

   def logEvent(self, eventName, eventDescr = ''):
      if eventName == 'StartAq':
          eventDescr = '%d' % self.spooler.imNum
      self.tq.logQueueEvent(self.queueName, (eventName, eventDescr, sp.timeFcn()))
      

class Spooler(sp.Spooler):
   #self.spooler = QueueSpooler.Spooler(self.scope, self.queueName, self.scope.pa, protocol, self, complevel=compLevel)
   def __init__(self, scope, filename, acquisator, protocol = p.NullProtocol, parent=None, complevel=2, complib='zlib'):
#       if 'PYME_TASKQUEUENAME' in os.environ.keys():
#            taskQueueName = os.environ['PYME_TASKQUEUENAME']
#       else:
#            taskQueueName = 'taskQueue'
       from PYME.misc.computerName import GetComputerName
       compName = GetComputerName()

       taskQueueName = 'TaskQueues.%s' % compName

       self.tq = Pyro.core.getProxyForURI('PYRONAME://' + taskQueueName)
       self.tq._setOneway(['postTask', 'postTasks', 'addQueueEvents', 'setQueueMetaData', 'logQueueEvent'])

       self.seriesName = filename
       self.buffer = []
       self.buflen = 30

       self.tq.createQueue('HDFTaskQueue',
                           self.seriesName, 
                           filename, 
                           frameSize = (scope.cam.GetPicWidth(), 
                                        scope.cam.GetPicHeight()), 
                           complevel=complevel, complib=complib)

       self.md = MetaDataHandler.QueueMDHandler(self.tq, self.seriesName)
       self.evtLogger = EventLogger(self, scope, self.tq, self.seriesName)

       sp.Spooler.__init__(self, scope, filename, acquisator, protocol, parent)
   
   def Tick(self, caller):
      #self.tq.postTask(cSMI.CDataStack_AsArray(caller.ds, 0).reshape(1,self.scope.cam.GetPicWidth(),self.scope.cam.GetPicHeight()), self.seriesName)
      self.buffer.append(caller.dsa.reshape(1,self.scope.cam.GetPicWidth(),self.scope.cam.GetPicHeight()).copy())

      if self.imNum == 0: #first frame
          self.md.setEntry('imageID', fileID.genFrameID(self.buffer[-1].squeeze()))

      if len(self.buffer) >= self.buflen:
          self.FlushBuffer()

      sp.Spooler.Tick(self, caller)
      
   def FlushBuffer(self):
      t1 = time.time()
      self.tq.postTasks(self.buffer, self.seriesName)
      #print time.time() -t1
      self.buffer = []



   
