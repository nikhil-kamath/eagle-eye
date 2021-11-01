from kivy.app import App
from kivy.uix.video import Video
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class myopia_diagnosis(App):
    def build(self):
        video = Video(source = './CVModules/assets/tom_brady_demo.MOV')
        video.state = "play"
        video.allow_stretch = True

        return video

if __name__ == '__main__':
    window = myopia_diagnosis()
    window.run()