import wx
import os
import shutil
import zipfile
import json
import winreg
from generator import generate_modpack


class ModpackGenerator(wx.Frame):
    def __init__(self):
        super().__init__(None)

         # Set window title, size and icon
        self.SetTitle("Minecraft Modpack Generator")
        self.SetIcon(wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO))
        self.SetSize((900, 450))
        self.SetMinSize((900, 450))

        # Create UI
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Minecraft folder input
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        mc_folder_label = wx.StaticText(panel, label="Minecraft Folder:")
        hbox1.Add(mc_folder_label, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.mc_folder_ctrl = wx.DirPickerCtrl(panel, message="Select Minecraft folder", style=wx.DIRP_USE_TEXTCTRL)
        hbox1.Add(self.mc_folder_ctrl, wx.EXPAND)
        vbox.Add(hbox1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)
        self.name_label = wx.StaticText(panel, label="Modpack Name:")
        hbox1.Add(self.name_label, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.name_ctrl = wx.TextCtrl(panel)
        hbox1.Add(self.name_ctrl, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)


        # Version selection
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        version_label = wx.StaticText(panel, label="Minecraft Version:")
        hbox2.Add(version_label, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.version_ctrl = wx.ComboBox(panel, style=wx.CB_READONLY)
        hbox2.Add(self.version_ctrl, wx.EXPAND)

        vbox.Add(hbox2, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)

        # Generate button
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        generate_button = wx.Button(panel, label="Generate")
        hbox3.Add(generate_button, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        vbox.Add(hbox3, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        desktop_path = winreg.QueryValueEx(key, "Desktop")[0]

        self.output_dir_label = wx.StaticText(panel, label="Output Directory:")
        hbox2.Add(self.output_dir_label, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.output_dir_picker = wx.DirPickerCtrl(panel, path=desktop_path)
        hbox2.Add(self.output_dir_picker, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)



        # Bind events
        self.Bind(wx.EVT_BUTTON, self.on_generate, generate_button)
        self.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_select_mc_folder, self.mc_folder_ctrl)
        self.Bind(wx.EVT_BUTTON, self.on_generate, generate_button)

        panel.SetSizer(vbox)

        self.SetSize((400, 200))
        self.Centre()
        self.Show(True)
    
    def on_select_mc_folder(self, event):
        mc_folder = self.mc_folder_ctrl.GetPath()
        if not mc_folder:
            mc_folder = os.path.expanduser("~")
        dlg = wx.DirDialog(self, "Choose Minecraft Folder", defaultPath=mc_folder, style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            mc_folder = dlg.GetPath()
            if os.path.basename(mc_folder) == '.minecraft':
                self.mc_folder_ctrl.SetPath(mc_folder)
                versions_dir = os.path.join(mc_folder, 'versions')
                self.populate_version_list(versions_dir)
            else:
                wx.MessageBox("The selected folder is not a '.minecraft' folder.", "Error",
                                wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def populate_version_list(self, versions_dir):
        version_list = [f for f in os.listdir(versions_dir) if os.path.isdir(os.path.join(versions_dir, f))]
        self.version_ctrl.Clear()
        for version in version_list:
            version_path = os.path.join(versions_dir, version)
            json_file = os.path.join(version_path, f'{version}.json')
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'libraries' in data:
                        for library in data['libraries']:
                            if 'name' in library:
                                if 'net.fabricmc:fabric-loader' in library['name']:
                                    version += "(Fabric)"
                                    break
                                elif 'net.minecraftforge:forge' in library['name']:
                                    version += "(Forge)"
                                    break
                        else:
                            version += " (Vanilla)"
                    else:
                        version += " (Vanilla)"
            else:
                version += " (Unknown)"

            self.version_ctrl.Append(version)
        self.version_ctrl.SetSelection(0)

    def on_generate(self, event):
        name = self.name_ctrl.GetValue()
        version = self.version_ctrl.GetValue()
        version = version.replace("(Forge)", "").replace("(Fabric)", "").strip()
        minecraft_folder = self.mc_folder_ctrl.GetPath()
        ## 在minecraft_folder后添加/version/
        mods_dir = os.path.join(minecraft_folder, 'versions', version, 'mods')
        output_dir = self.output_dir_picker.GetPath()
        print(version, minecraft_folder)

        zip_file = generate_modpack(name, version, mods_dir, output_dir)

if __name__ == '__main__':
    app = wx.App()
    ModpackGenerator()
    app.MainLoop()
