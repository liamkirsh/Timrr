import wx
import agents
import taskbar

class MainWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.tbicon = taskbar.TaskBarIcon(self)

       	"""
        self.panel = wx.Panel(self)
        self.button = wx.Button(self.panel, label="Test")

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.button)

        self.panel.SetSizerAndFit(self.sizer)
        self.Show()
        """

app = wx.App(False)
win = MainWindow(None)
agents.run_all()
app.MainLoop()
