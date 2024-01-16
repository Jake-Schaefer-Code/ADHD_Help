from moviepy.editor import VideoFileClip, CompositeVideoClip
import whisper
from tqdm import tqdm
import textwrap
from PIL import Image, ImageDraw, ImageFont
from moviepy.video.VideoClip import ImageClip
from moviepy.video import fx
import numpy as np
import random
import speech_recognition as sr
from pydub import AudioSegment
import syllables

NUM_CHARS_IN_LINE = 18
SUBTITLE_PERCENT_SCREEN = 0.75

# TODO
# add emojis
# make the text pulse each time a word is highlighted
class VideoTranscriber:
    def __init__(self, model_path, video_path, filename):
        self.model = whisper.load_model(model_path)
        self.video_path = video_path
        self.audio_path = ''
        self.text_array = []
        self.word_array = []
        self.subtitle_clips = []
        self.frames = []
        self.fps = 0
        self.char_width = 0
        self.video = VideoFileClip(video_path)
        
        self.position = ('center', self.video.h*0.75)
        self.max_width = int(self.video.w * SUBTITLE_PERCENT_SCREEN)

        self.font_size = 1.5 * self.video.w / NUM_CHARS_IN_LINE
        print(self.font_size)

        self.spacing = self.video.w // 180
        self.v_spacing = self.video.w // 108
    
        #self.max_line_length = 24
        print(self.video.w, self.video.h)
        print(self.max_width)
        print(self.font_size)

        self.file_name = filename
        

    def transcribe_video(self):
        print('Transcribing Video')
        result = self.model.transcribe(self.audio_path)
        #result = self.model.transcribe("audio_downloads/Cant_Take_My_Eyes_Off_Of_You.mp3")
        text = result['segments'][0]['text']
        for seg in tqdm(result['segments']):
            text = seg['text'].replace('.','')
            text = text.replace(',','')
            end = seg['end']
            start = seg['start']
            line_array = [text.upper(), start, end]
            self.text_array.append(line_array)

        print('Transcription Complete')

    def extract_audio(self):
        print('Extracting Audio')
        output_audio_path='test_videos/{}.mp3'.format(self.file_name)
        video = VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)
        self.audio_path = output_audio_path

    def extract_frames(self, output_folder=None):
        print('extracting frames')
        font = '/Users/jakeschaefer/Desktop/code/Fun/files/Montserrat-Black.ttf'
        
        for n, subtitle in enumerate(self.text_array):
            text, start, end = subtitle
            print("self.text_array[{}] = [\"{}\", {}, {}]".format(n, text, start, end))
            lines = self.split_line(text)
            duration_per_word = (end - start) / len(text.split())
            duration_per_line = (end - start) / len(lines)
            
            syllables_in_text = 0
            for word in text.split():
                est = syllables.estimate(word)
                syllables_in_text += est
            duration_per_syllable = (end - start) / syllables_in_text


            total_syllables = 0
            for i, line in enumerate(lines):
                index_in_text = 0
                
                syllables_in_line = 0
                words = line.split()
                for i, word in enumerate(words):
                    if word == "SHWET" or word == "J-SLET":
                        words[i] = "SCHLATT"
                        word = words[i]
                    est = syllables.estimate(word)
                    syllables_in_line+=est
                
                line_start = start + total_syllables * duration_per_syllable
                line_end = line_start + syllables_in_line * duration_per_syllable
                total_syllables += syllables_in_line

                """line_start = start + num_words * duration_per_word
                cur_words = len(line.split())
                line_end = line_start + duration_per_word * cur_words
                num_words += cur_words"""
                """line_start = start + i * duration_per_line
                line_end = line_start + duration_per_line
                dur_per_word = (line_end - line_start) / len(words)"""

                total_syl = 0
                syl = []
                #sent = ''
                for word in words:
                    est = syllables.estimate(word)
                    syl.append(est)
                    total_syl+=est
                    #sent += word + ' '
                
                line = ' '.join(line.split())
                print(len(line),self.max_width / self.font_size)
                if len(line) > NUM_CHARS_IN_LINE:
                    line = textwrap.wrap(line, int(self.max_width / self.font_size), break_long_words=False, replace_whitespace=False)
                else:
                    line = [line]
                print(line)

                #dur_per_char = (line_end - line_start) / len(sent)
                #avg_dir = (line_end - line_start) / ((total_syl + len(' '.join(words)))/2)
                #cur_char = 0 
                dur_per_syl = (line_end - line_start) / total_syl
                cur_syl = 0
                
                """normal_font_size = int(self.font_size)
                highlight_font_size = int(self.font_size * 1.2)
                font_normal = ImageFont.truetype(font, normal_font_size)
                font_highlight = ImageFont.truetype(font, highlight_font_size)
                line_images = []
                for l in line:
                    word_fonts = [font_normal for _ in range(len(words))] # maybe just in words
                    words = l.split()
                    line_width = 0
                    height = 0
                    for word in words:
                        width, line_height = ImageDraw.Draw(Image.new('RGB', (1,1))).textsize(word, font=font_highlight)
                        line_width += width #+ 2*self.spacing  
                        height = max(height+ 2*self.spacing, line_height+ 2*self.spacing)

                    img_line = Image.new('RGBA', (self.video.w, height), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(img_line)

                    start_x = (self.video.w - line_width)//2 # Centers the text
                    for highlight_index, word in enumerate(words):
                        word_start = line_start + cur_syl * dur_per_syl
                        word_fonts[highlight_index] = font_highlight
                        num = random.randrange(0,99)
                        if num < 10:
                            color = (248,225,11)
                        else:
                            color = (6,214,40)
                        for i, word2 in enumerate(words):
                            if i == highlight_index:
                                font = font_highlight
                                draw.text((start_x, -self.v_spacing), word, font=font, fill="black", stroke_fill="black",stroke_width=normal_font_size//6)
                                draw.text((start_x, -self.v_spacing), word, font=font,  fill=color)
                            else:
                                font = font_normal
                                draw.text((start_x, 0), word, font=font,  fill="black", stroke_fill="black",stroke_width=normal_font_size//6)
                                draw.text((start_x, 0), word, font=font, fill="white")
                            start_x += draw.textsize(word, font=font)[0] + self.spacing
                        line_images.append(img_line)


                        word_fonts[highlight_index] = font_normal

                max_height = sum(img.size[1] for img in line_images)
                total_img = Image.new('RGBA', (self.video.w, max_height+self.v_spacing), (0,0,0,0))
            
                y_offset = 0
                for img in line_images:
                    total_img.paste(img, (0, y_offset))
                    y_offset += img.size[1]"""


                for j, word in enumerate(words):
                    word_start = line_start + cur_syl * dur_per_syl

                    # TODO EMOJI CODE
                    emoji = False
                    if emoji:
                        emoji_char = ""
                        emojiimg = self.create_text_image(emoji_char, j, font, int(self.font_size), int(self.font_size * 1.2), emoji=True)
                        emojiclip = ImageClip(emojiimg).set_duration(dur_per_syl * syl[j]).set_start(word_start)
                        emojiclip = emojiclip.set_pos(self.position)
                        self.frames.append(emojiclip)

                    img = self.create_text_image(line, j, font, int(self.font_size), int(self.font_size * 1.2))
                    clip = ImageClip(img).set_duration(dur_per_syl * syl[j]).set_start(word_start)
                    cur_syl += syl[j]

                    """word_start = line_start + cur_char
                    img = self.create_text_image(line, j, font, 90, 110)
                    clip = ImageClip(img).set_duration((len(word) + 1) * dur_per_char).set_start(word_start)
                    cur_char += (len(word) + 1) * dur_per_char"""
                    """word_start = line_start + j * dur_per_word
                    img = self.create_text_image(line, j, font, 90, 110)
                    clip = ImageClip(img).set_duration(dur_per_word).set_start(word_start)
                    #print(word_start, dur_per_word+word_start)"""

                    clip = clip.set_pos(self.position)
                    self.frames.append(clip)

                """line_start = start + i * duration_per_line
                line_end = line_start + duration_per_line
                wrapped_text = self.wrap_text(line, self.max_width)
                txt_clip = TextClip(wrapped_text, fontsize = 90, color = 'black', font=font, stroke_color='black', stroke_width=30)
                txt_clip = txt_clip.set_duration(duration_per_line).set_start(line_start)
                txt_clip = txt_clip.set_pos(self.position)
                self.subtitle_clips.append(txt_clip)
                txt_clip2 = TextClip(wrapped_text, fontsize = 90, color = 'white', font=font, stroke_color='white', stroke_width=8)
                txt_clip2 = txt_clip2.set_duration(duration_per_line).set_start(line_start)
                txt_clip2 = txt_clip2.set_pos(self.position)
                self.subtitle_clips.append(txt_clip2)

                words = line.split()
                dur_per_word = (end - start) / len(words)
                for j, word in enumerate(words):
                    word_start = line_start + j * dur_per_word
                    new_words = [' ' * len(w) if w != word else word for w in words]
                    new_text = ''
                    for w in new_words:
                        new_text = w + ' '
                    txt_cliph = TextClip(new_text, fontsize = 110, color = 'green', font=font, stroke_color='green', stroke_width=30)
                    txt_cliph = txt_cliph.set_duration(dur_per_word).set_start(word_start)    
                    txt_cliph = txt_cliph.set_pos(self.position)
                    self.subtitle_clips.append(txt_cliph)"""
                
        print('frames extracted')


    def create_text_image(self, line, h_word_index, font_path, normal_size, highlight_size, emoji=False):
        font_normal = ImageFont.truetype(font_path, normal_size)
        font_highlight = ImageFont.truetype(font_path, highlight_size)

        line_images = []
        h_index = 0
        for l in line:
            line_width = 0
            height = 0
            words = l.split()

            for i, word in enumerate(words):
                if h_index == h_word_index:
                    font = font_highlight
                    words[i] = '*' + word + '*'
                else:
                    font = font_normal
                h_index += 1
                width, line_height = ImageDraw.Draw(Image.new('RGB', (1,1))).textsize(word, font=font)
                line_width += width + 2*self.spacing
                height = max(height+10, line_height+10)
                
            
            img_line = Image.new('RGBA', (self.video.w, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img_line)
            
            x = (self.video.w - line_width)//2
            #print(line_width)
            for i, word in enumerate(words):
                if word[0] == '*' and word[-1] == '*':
                    font = font_highlight
                    num = random.randrange(0,99)
                    if num < 10:
                        color = (248,225,11)
                    else:
                        color = (6,214,40)
                    word = word[1:-1]
                    draw.text((x, -self.v_spacing), word, font=font, fill="black", stroke_fill="black",stroke_width=normal_size//6)
                    draw.text((x, -self.v_spacing), word, font=font,  fill=color)
                else:
                    font = font_normal
                    color = "white"
                    draw.text((x, 0), word, font=font,  fill="black", stroke_fill="black",stroke_width=normal_size//6)
                    draw.text((x, 0), word, font=font, fill=color)
                x += draw.textsize(word, font=font)[0] + self.spacing

            line_images.append(img_line)

        max_height = sum(img.size[1] for img in line_images)
        total_img = Image.new('RGBA', (self.video.w, max_height+self.v_spacing), (0,0,0,0))
    
        y_offset = 0
        for img in line_images:
            total_img.paste(img, (0, y_offset))
            y_offset += img.size[1]

        return np.array(total_img)
    
    def split_line(self, text, max_length=24):
        words = text.split()
        lines = []
        current_line = words[0]
        for word in words[1:]:
            if len(current_line) + len(word) + 1 <= max_length:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return lines

    def wrap_text(self, text, max_width):
        return textwrap.fill(text, max_width)

    def create_video(self, editscript = False):
        print('creating video')
        if editscript:
            """self.text_array[0] = ["YOU'RE JUST TOO GOOD TO BE TRUE", 15.5, 19.5]
            self.text_array[1] = ["CAN'T TAKE MY EYES OFF OF YOU", 20.0, 23.0]
            self.text_array[2] = ["YOU'D BE LIKE HEAVEN TO TOUCH", 24.0, 27.0]
            self.text_array[3] = ["I WANT TO HOLD YOU SO MUCH", 28.0, 31.0]
            self.text_array[4] = ["AT LONG LAST LOVE HAS ARRIVED", 32.0, 35.0]
            self.text_array[5] = ["AND I THANK GOD I'M ALIVE", 36.0, 38.5]
            self.text_array[6] = [" YOU'RE JUST TOO GOOD TO BE TRUE", 40.0, 42.0]
            self.text_array[7] = [" CAN'T TAKE MY EYES OFF OF YOU", 43.0, 46.0]
            self.text_array[8] = ["PARDON THE WAY THAT I STARE", 47.0, 50.5]
            self.text_array[9] = [" THERE'S NOTHING ELSE TO COMPARE", 51.0, 54.5]
            self.text_array[10] = ["THIS SIDE OF YOU LEAVES ME WEAK", 55.0, 58.0]
            self.text_array[11] = ["THERE ARE NO WORDS LEFT TO SPEAK", 59.0, 62.0]
            self.text_array[12] = ["BUT IF YOU FEEL LIKE I FEEL", 63.0, 66.0]
            self.text_array[13] = [" PLEASE LET ME KNOW THAT IT'S REAL", 66.5, 69.5]
            self.text_array[14] = [" YOU'RE JUST TOO GOOD TO BE TRUE", 70.4, 73.0]
            self.text_array[15] = [" CAN'T TAKE MY EYES OFF OF YOU", 74.0, 77.0]
            self.text_array[16] = ["...", 86.0, 86.1]
            self.text_array[17] = [" I LOVE YOU BABY", 95.0, 98.0]
            self.text_array[18] = ["AND IF IT'S QUITE ALRIGHT I NEED YOU BABY", 98.0, 102.0]
            self.text_array[19] = ["TO WARM A LONELY NIGHT", 102.0,104.0]
            self.text_array[20] = ["I LOVE YA BABY",104.0, 106.0]
            self.text_array[22] = [" OH PRETTY BABY", 110.5, 113.0]
            self.text_array[23] = ["DONT BRING ME DOWN I PRAY", 113.5, 115.0]
            self.text_array[24] = ["OH PRETTY BABY", 115.0, 117.0]
            self.text_array[25] = ["NOW THAT I FOUND YOU STAY", 117.0, 119.2]
            self.text_array[26] = [" LET ME LOVE YOU BABY", 119.2, 122.6]
            self.text_array[27] = [" LET ME LOVE YOU", 122.8, 126.0]
            self.text_array[29] = [" CAN'T TAKE MY EYES OFF OF YOU", 130.5, 133.5]
            self.text_array[30] = [" YOU'D BE LIKE HEAVEN TO TOUCH", 134.5, 138.0]
            self.text_array[31] = [" I WANT TO HOLD YOU SO MUCH", 138.5, 142.0]
            self.text_array[33] = ["AND I THANK GOD I'M ALIVE", 146.0, 150.0]
            self.text_array[34] = [" YOU'RE JUST TOO GOOD TO BE TRUE", 150.0, 153.0]
            self.text_array[35] = [" CAN'T TAKE MY EYES OFF OF YOU", 154.0, 157.0]
            self.text_array[36] = ["...", 158.0, 158.1]
            self.text_array[37] = [" I LOVE YOU BABY", 167.0, 169.5]
            self.text_array[39] = ["I NEED YOU BABY", 172.0, 174.0]
            self.text_array[40] = ["TO WARM A LONELY NIGHT", 174.0, 176.0]
            self.text_array[41] = [" I LOVE YA BABY", 176.0, 178.0]
            self.text_array[43] = [" OH PRETTY BABY", 182.5, 185.0]
            self.text_array[44] = ["DONT BRING ME DOWN I PRAY", 185.5, 187.5]
            self.text_array[45] = ["OH PRETTY BABY", 187.5,189.0]
            self.text_array[46] = ["NOW THAT I FOUND YOU STAY", 189.5, 191.0]
            self.text_array[47] = [" OH PRETTY BABY", 192.0, 194.0]"""


            #self.text_array[5] = ["YOU'RE JUST TOO GOOD TO BE TRUE CAN'T TAKE MY EYES OFF OF YOU", 70.0, 77.5]
            #self.text_array[6] = ["I LOVE YOU BABY AND IF IT'S QUITE ALRIGHT I NEED YOU BABY TO WARM THE MORNING LIGHT I LOVE YOUR BABY", 95.0, 106.0]
            #self.text_array[7] = ["I LOVE YOU BABY HANDS IT THE TITLE RIGHT I NEED YOUR BABY TO WARM THE MORNING LIGHT I LOVE YOUR BABY", 95.0, 106.0]
            self.text_array = [["LET'S TRY DOES SCHLATT DOES JSCHLATT HAVE A GUN?", 0.0, 3.0],
                                ["WOULDN'T YOU LIKE TO KNOW?", 5.5, 6.5],
                                ["I DON'T HAVE TO FUCKING TELL YOU", 8.0,9.5],
                                ["DO I HAVE TO TELL YOU?",9.5,10.5 ],
                                ["YOU WANT TO FIND OUT?", 11.200000000000001, 12.0],
                                ["NO COME ON BY FIND OUT",12.0, 13.3],
                                ["NO NO NO NO COME ON", 13.3, 14.5],
                                ["COME ON GIVE ME A VISIT", 14.5, 16.0]]
        self.extract_frames()
        final_video = CompositeVideoClip([self.video] + self.subtitle_clips)
        final_video = CompositeVideoClip([self.video] + self.frames).set_duration(self.text_array[-1][-1])
        final_video.write_videofile('output_vids/{}.mp4'.format(self.file_name))

model_path = 'base'
#video_path = "test_videos/Jschlatt_Cant_Celebrate_His_Birthday_Ever_Again!!!.mp4"
#filename = "Jschlatt_Cant_Celebrate_His_Birthday_Ever_Again_Subtitles"
filename = "Does_jschlatt_own_a_gun"
video_path = "test_videos/Does_jschlatt_own_a_gunmp4.mp4"
output_video_path = 'test_videos/{}.mp4'.format(filename)
editscript = True

# TODO remove audio files when done
                
transcriber = VideoTranscriber(model_path, video_path, filename)
transcriber.extract_audio()
transcriber.transcribe_video()
transcriber.create_video(editscript)