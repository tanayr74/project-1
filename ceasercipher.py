import wx
import pyperclip
import speech_recognition as sr
import threading

class CaesarCipherFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Caesar Cipher Tool', size=(750, 800))
        
        # Set black background
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        # Voice recording state
        self.is_recording = False
        self.recording_thread = None
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        main_sizer.AddSpacer(20)
        
        # Title
        title = wx.StaticText(panel, label='🔐 Caesar Cipher Tool')
        title_font = wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(0, 255, 0))
        main_sizer.Add(title, 0, wx.CENTER, 0)
        
        main_sizer.AddSpacer(5)
        
        # Green separator line
        line1 = wx.Panel(panel, size=(700, 3))
        line1.SetBackgroundColour(wx.Colour(0, 255, 0))
        main_sizer.Add(line1, 0, wx.CENTER, 0)
        
        main_sizer.AddSpacer(15)
        
        # Input section with border
        input_box = wx.StaticBox(panel, label='Input', style=wx.BORDER_SIMPLE)
        input_box.SetForegroundColour(wx.Colour(0, 255, 0))
        input_box_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        input_box.SetFont(input_box_font)
        
        input_box_sizer = wx.StaticBoxSizer(input_box, wx.VERTICAL)
        
        self.input_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.BORDER_SIMPLE)
        self.input_text.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.input_text.SetForegroundColour(wx.Colour(255, 255, 255))
        input_text_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.input_text.SetFont(input_text_font)
        self.input_text.Bind(wx.EVT_TEXT, self.on_text_change)
        input_box_sizer.Add(self.input_text, 1, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(input_box_sizer, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 20)
        
        main_sizer.AddSpacer(10)
        
        # Input buttons row (Import, Voice, Clear)
        input_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_btn_sizer.AddSpacer(20)
        
        import_btn = wx.Button(panel, label='📁 Import', size=(100, 30))
        import_btn.SetBackgroundColour(wx.Colour(255, 255, 255))
        import_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        btn_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        import_btn.SetFont(btn_font)
        import_btn.Bind(wx.EVT_BUTTON, self.on_import)
        input_btn_sizer.Add(import_btn, 0)
        
        input_btn_sizer.AddSpacer(10)
        
        self.voice_btn = wx.Button(panel, label='🎤 Voice', size=(100, 30))
        self.voice_btn.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.voice_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.voice_btn.SetFont(btn_font)
        self.voice_btn.Bind(wx.EVT_BUTTON, self.on_voice_toggle)
        input_btn_sizer.Add(self.voice_btn, 0)
        
        input_btn_sizer.AddSpacer(10)
        
        clear_input_btn = wx.Button(panel, label='🗑️ Clear', size=(100, 30))
        clear_input_btn.SetBackgroundColour(wx.Colour(255, 255, 255))
        clear_input_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        clear_input_btn.SetFont(btn_font)
        clear_input_btn.Bind(wx.EVT_BUTTON, self.on_clear_input)
        input_btn_sizer.Add(clear_input_btn, 0)
        
        main_sizer.Add(input_btn_sizer, 0, wx.ALL, 5)
        
        main_sizer.AddSpacer(5)
        
        # Control section (Shift, Mode)
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Shift with textbox
        shift_label = wx.StaticText(panel, label='🔢 Shift:')
        shift_label.SetForegroundColour(wx.Colour(0, 255, 0))
        shift_label_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        shift_label.SetFont(shift_label_font)
        control_sizer.Add(shift_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)
        
        control_sizer.AddSpacer(10)
        
        self.shift_input = wx.TextCtrl(panel, value='', size=(80, 30), style=wx.TE_CENTER | wx.BORDER_SIMPLE)
        self.shift_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.shift_input.SetForegroundColour(wx.Colour(0, 0, 0))
        shift_input_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.shift_input.SetFont(shift_input_font)
        self.shift_input.Bind(wx.EVT_TEXT, self.on_shift_change)
        control_sizer.Add(self.shift_input, 0, wx.ALIGN_CENTER_VERTICAL)
        
        control_sizer.AddSpacer(30)
        
        # Mode
        mode_label = wx.StaticText(panel, label='Mode:')
        mode_label.SetForegroundColour(wx.Colour(0, 255, 0))
        mode_label.SetFont(shift_label_font)
        control_sizer.Add(mode_label, 0, wx.ALIGN_CENTER_VERTICAL)
        
        control_sizer.AddSpacer(15)
        
        self.encode_btn = wx.Button(panel, label='🔒 Encode', size=(110, 35))
        self.encode_btn.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.encode_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        button_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.encode_btn.SetFont(button_font)
        self.encode_btn.Bind(wx.EVT_BUTTON, self.on_encode)
        control_sizer.Add(self.encode_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        
        control_sizer.AddSpacer(15)
        
        self.decode_btn = wx.Button(panel, label='🔑 Decode', size=(110, 35))
        self.decode_btn.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.decode_btn.SetForegroundColour(wx.Colour(120, 120, 120))
        self.decode_btn.SetFont(button_font)
        self.decode_btn.Bind(wx.EVT_BUTTON, self.on_decode)
        control_sizer.Add(self.decode_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(control_sizer, 0, wx.ALL, 5)
        
        main_sizer.AddSpacer(10)
        
        # Output section with border
        output_box = wx.StaticBox(panel, label='Output', style=wx.BORDER_SIMPLE)
        output_box.SetForegroundColour(wx.Colour(0, 255, 0))
        output_box.SetFont(input_box_font)
        
        output_box_sizer = wx.StaticBoxSizer(output_box, wx.VERTICAL)
        
        self.output_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE)
        self.output_text.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.output_text.SetForegroundColour(wx.Colour(255, 255, 255))
        self.output_text.SetFont(input_text_font)
        output_box_sizer.Add(self.output_text, 1, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(output_box_sizer, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 20)
        
        main_sizer.AddSpacer(10)
        
        # Output buttons row (Copy, Export)
        output_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_btn_sizer.AddSpacer(20)
        
        copy_btn = wx.Button(panel, label='📋 Copy', size=(100, 30))
        copy_btn.SetBackgroundColour(wx.Colour(255, 255, 255))
        copy_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        copy_btn.SetFont(btn_font)
        copy_btn.Bind(wx.EVT_BUTTON, self.on_copy)
        output_btn_sizer.Add(copy_btn, 0)
        
        output_btn_sizer.AddSpacer(10)
        
        export_btn = wx.Button(panel, label='💾 Export', size=(100, 30))
        export_btn.SetBackgroundColour(wx.Colour(255, 255, 255))
        export_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        export_btn.SetFont(btn_font)
        export_btn.Bind(wx.EVT_BUTTON, self.on_export)
        output_btn_sizer.Add(export_btn, 0)
        
        main_sizer.Add(output_btn_sizer, 0, wx.ALL, 5)
        
        main_sizer.AddSpacer(10)
        
        panel.SetSizer(main_sizer)
        
        # Initialize mode
        self.mode = 'encode'
        self.update_mode_buttons()
        
        self.Centre()
        self.Show()
    
    def caesar_cipher(self, text, shift, encode=True):
        """Caesar cipher encryption/decryption"""
        if not text:
            return ''
        
        if not encode:
            shift = -shift
        
        result = []
        for char in text:
            if char.isalpha():
                ascii_offset = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - ascii_offset + shift) % 26
                result.append(chr(shifted + ascii_offset))
            else:
                result.append(char)
        
        return ''.join(result)
    
    def on_encode(self, event):
        """Switch to encode mode"""
        self.mode = 'encode'
        self.update_mode_buttons()
        self.update_output()
    
    def on_decode(self, event):
        """Switch to decode mode"""
        self.mode = 'decode'
        self.update_mode_buttons()
        self.update_output()
    
    def update_mode_buttons(self):
        """Update button appearance based on selected mode"""
        if self.mode == 'encode':
            self.encode_btn.SetForegroundColour(wx.Colour(0, 0, 0))
            self.decode_btn.SetForegroundColour(wx.Colour(120, 120, 120))
        else:
            self.encode_btn.SetForegroundColour(wx.Colour(120, 120, 120))
            self.decode_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.encode_btn.Refresh()
        self.decode_btn.Refresh()
    
    def on_text_change(self, event):
        """Handle text changes in input field"""
        self.update_output()
    
    def on_shift_change(self, event):
        """Handle shift textbox changes"""
        self.update_output()
    
    def update_output(self):
        """Update output based on input text and shift value"""
        input_val = self.input_text.GetValue()
        shift_val = self.shift_input.GetValue().strip()
        
        # Handle empty shift value
        if not shift_val:
            self.output_text.SetValue('')
            return
        
        # Validate shift is a number
        try:
            shift = int(shift_val)
        except ValueError:
            self.output_text.SetValue('Error: Shift must be a valid integer')
            return
        
        encode = (self.mode == 'encode')
        output = self.caesar_cipher(input_val, shift, encode)
        self.output_text.SetValue(output)
    
    def on_copy(self, event):
        """Copy output to clipboard"""
        output_text = self.output_text.GetValue()
        if output_text:
            try:
                pyperclip.copy(output_text)
                wx.MessageBox('Output copied to clipboard!', 'Success', wx.OK | wx.ICON_INFORMATION)
            except:
                wx.MessageBox('Failed to copy to clipboard', 'Error', wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox('Nothing to copy!', 'Info', wx.OK | wx.ICON_INFORMATION)
    
    def on_clear_input(self, event):
        """Clear input text box"""
        self.input_text.SetValue('')
    
    def on_import(self, event):
        """Import text from file"""
        with wx.FileDialog(self, "Import Text File",
                          wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.input_text.SetValue(content)
                wx.MessageBox('File imported successfully!', 'Success', wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f'Failed to import file: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)
    
    def on_export(self, event):
        """Export output to file"""
        output_text = self.output_text.GetValue()
        if not output_text:
            wx.MessageBox('Nothing to export!', 'Info', wx.OK | wx.ICON_INFORMATION)
            return
        
        with wx.FileDialog(self, "Export Text File",
                          wildcard="Text files (*.txt)|*.txt",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w', encoding='utf-8') as file:
                    file.write(output_text)
                wx.MessageBox('File exported successfully!', 'Success', wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f'Failed to export file: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)
    
    def on_voice_toggle(self, event):
        """Toggle voice recording on/off"""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.voice_btn.SetLabel('⏹️ Stop')
            self.voice_btn.SetBackgroundColour(wx.Colour(255, 100, 100))  # Red background
            self.voice_btn.Refresh()
            self.recording_thread = threading.Thread(target=self.continuous_voice_recognition, daemon=True)
            self.recording_thread.start()
        else:
            # Stop recording
            self.is_recording = False
            self.voice_btn.SetLabel('🎤 Voice')
            self.voice_btn.SetBackgroundColour(wx.Colour(255, 255, 255))  # White background
            self.voice_btn.Refresh()
    
    def continuous_voice_recognition(self):
        """Continuously recognize speech and update input text"""
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 4000
        recognizer.dynamic_energy_threshold = True
        
        try:
            with sr.Microphone() as source:
                wx.CallAfter(self.append_status, "🎤 Listening... Speak now!")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                while self.is_recording:
                    try:
                        # Listen for audio with short timeout
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        # Try to recognize speech
                        text = recognizer.recognize_google(audio)
                        
                        # Append recognized text to input box
                        if text:
                            current_text = self.input_text.GetValue()
                            if current_text and not current_text.endswith(' '):
                                text = ' ' + text
                            wx.CallAfter(self.input_text.SetValue, current_text + text)
                    
                    except sr.WaitTimeoutError:
                        # Timeout - continue listening
                        continue
                    except sr.UnknownValueError:
                        # Could not understand audio - continue listening
                        continue
                    except sr.RequestError as e:
                        wx.CallAfter(wx.MessageBox, f'Recognition service error: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)
                        break
                
        except Exception as e:
            wx.CallAfter(wx.MessageBox, f'Microphone error: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)
        finally:
            wx.CallAfter(self.stop_recording_cleanup)
    
    def append_status(self, message):
        """Display status message (optional - can be removed if not needed)"""
        pass
    
    def stop_recording_cleanup(self):
        """Cleanup when recording stops"""
        if self.is_recording:
            self.is_recording = False
            self.voice_btn.SetLabel('🎤 Voice')
            self.voice_btn.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.voice_btn.Refresh()

if __name__ == '__main__':
    app = wx.App()
    frame = CaesarCipherFrame()
    app.MainLoop()
